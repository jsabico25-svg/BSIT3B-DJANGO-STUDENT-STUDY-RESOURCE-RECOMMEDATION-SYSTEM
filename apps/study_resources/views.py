from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.core.validators import URLValidator
from django.db.models import Avg, Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

from apps.subject.models import Subject

from .models import StudyResource

MAX_TITLE_LENGTH = 200
MAX_TYPE_LENGTH = 50
DIFFICULTIES = ['Beginner', 'Intermediate', 'Advanced']


@login_required(login_url='login')
def resource_list_page(request):
    query = request.GET.get('q', '').strip()
    subject_id = request.GET.get('subject', '').strip()
    resource_type = request.GET.get('type', '').strip()
    difficulty = request.GET.get('difficulty', '').strip()

    resources = StudyResource.objects.select_related('subject').annotate(
        avg_rating=Avg('feedbacks__rating'),
        feedback_count=Count('feedbacks', distinct=True),
    )

    if query:
        resources = resources.filter(
            Q(title__icontains=query)
            | Q(description__icontains=query)
            | Q(subject__subject_name__icontains=query)
        )
    if subject_id.isdigit():
        resources = resources.filter(subject_id=subject_id)
    if resource_type:
        resources = resources.filter(resource_type=resource_type)
    if difficulty:
        resources = resources.filter(difficulty_level=difficulty)

    resources = resources.order_by('subject__subject_name', 'title')

    paginator = Paginator(resources, 10)
    page = paginator.get_page(request.GET.get('page', 1))

    context = {
        'resources': page,
        'subjects': Subject.objects.order_by('subject_name'),
        'types': list(
            StudyResource.objects.exclude(resource_type__isnull=True)
            .exclude(resource_type='')
            .values_list('resource_type', flat=True)
            .distinct()
            .order_by('resource_type')
        ),
        'difficulties': DIFFICULTIES,
        'query': query,
        'selected_subject': subject_id,
        'selected_type': resource_type,
        'selected_difficulty': difficulty,
    }
    return render(request, 'resources/list.html', context)


@login_required(login_url='login')
@require_POST
def resource_save_ajax(request):
    resource_id = request.POST.get('id')
    resource = (
        get_object_or_404(StudyResource, pk=resource_id)
        if resource_id
        else StudyResource()
    )
    is_update = bool(resource_id)

    subject_id = request.POST.get('subject', '').strip()
    title = request.POST.get('title', '').strip()
    description = request.POST.get('description', '').strip()
    resource_type = request.POST.get('resource_type', '').strip()
    resource_url = request.POST.get('resource_url', '').strip()
    difficulty_level = request.POST.get('difficulty_level', '').strip()

    if not subject_id.isdigit():
        return JsonResponse({'error': 'Please choose a subject.'}, status=400)
    subject = Subject.objects.filter(pk=subject_id).first()
    if subject is None:
        return JsonResponse({'error': 'That subject no longer exists.'}, status=400)

    if not title:
        return JsonResponse({'error': 'Title is required.'}, status=400)
    if len(title) > MAX_TITLE_LENGTH:
        return JsonResponse(
            {'error': f'Title must be {MAX_TITLE_LENGTH} characters or fewer.'},
            status=400,
        )
    if len(resource_type) > MAX_TYPE_LENGTH:
        return JsonResponse(
            {'error': f'Resource type must be {MAX_TYPE_LENGTH} characters or fewer.'},
            status=400,
        )
    if difficulty_level and difficulty_level not in DIFFICULTIES:
        return JsonResponse({'error': 'Invalid difficulty level.'}, status=400)
    if resource_url:
        try:
            URLValidator(schemes=['http', 'https'])(resource_url)
        except ValidationError:
            return JsonResponse(
                {'error': 'Enter a valid URL starting with http:// or https://.'},
                status=400,
            )

    resource.subject = subject
    resource.title = title
    resource.description = description or None
    resource.resource_type = resource_type or None
    resource.resource_url = resource_url or None
    resource.difficulty_level = difficulty_level or None
    resource.save()

    messages.success(
        request,
        f'Resource "{resource.title}" has been '
        f'{"updated" if is_update else "saved"} successfully.',
    )
    return JsonResponse({'status': 'success', 'id': resource.pk})


@login_required(login_url='login')
@require_POST
def resource_delete_ajax(request, pk):
    resource = get_object_or_404(StudyResource, pk=pk)
    title = resource.title
    resource.delete()
    messages.success(
        request,
        f'Resource "{title}" and its feedback/recommendations have been deleted.',
    )
    return JsonResponse({'status': 'deleted'})
