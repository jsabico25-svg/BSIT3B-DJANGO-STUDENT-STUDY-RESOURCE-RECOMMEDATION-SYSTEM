from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

from .models import Subject

MAX_NAME_LENGTH = 100


@login_required(login_url='login')
def subject_list_page(request):
    query = request.GET.get('q', '').strip()

    subjects = Subject.objects.annotate(
        resource_count=Count('resources', distinct=True),
        student_count=Count('student_subjects', distinct=True),
    ).order_by('subject_name')

    if query:
        subjects = subjects.filter(
            Q(subject_name__icontains=query) |
            Q(description__icontains=query)
        )

    paginator = Paginator(subjects, 10)
    page = paginator.get_page(request.GET.get('page', 1))

    return render(request, 'subjects/list.html', {
        'subjects': page,
        'query': query,
    })


@login_required(login_url='login')
@require_POST
def subject_save_ajax(request):
    subject_id = request.POST.get('id')
    subject = get_object_or_404(Subject, pk=subject_id) if subject_id else Subject()
    is_update = bool(subject_id)

    name = request.POST.get('subject_name', '').strip()
    description = request.POST.get('description', '').strip()

    if not name:
        return JsonResponse({'error': 'Subject name is required.'}, status=400)
    if len(name) > MAX_NAME_LENGTH:
        return JsonResponse(
            {'error': f'Subject name must be {MAX_NAME_LENGTH} characters or fewer.'},
            status=400,
        )

    duplicates = Subject.objects.filter(subject_name__iexact=name)
    if subject.pk:
        duplicates = duplicates.exclude(pk=subject.pk)
    if duplicates.exists():
        return JsonResponse({'error': 'That subject already exists.'}, status=400)

    subject.subject_name = name
    subject.description = description
    subject.save()

    messages.success(
        request,
        f'Subject "{subject.subject_name}" has been {"updated" if is_update else "saved"} successfully.',
    )
    return JsonResponse({'status': 'success', 'id': subject.pk})


@login_required(login_url='login')
@require_POST
def subject_delete_ajax(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    name = subject.subject_name
    subject.delete()
    messages.success(request, f'Subject "{name}" and its resources/enrollments have been deleted.')
    return JsonResponse({'status': 'deleted'})
