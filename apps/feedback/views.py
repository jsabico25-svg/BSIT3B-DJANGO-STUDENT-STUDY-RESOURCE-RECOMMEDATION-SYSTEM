from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

from apps.students.models import Student
from apps.study_resources.models import StudyResource

from .models import Feedback

RATING_CHOICES = range(1, 6)


@login_required(login_url='login')
def feedback_list_page(request):
    query = request.GET.get('q', '').strip()
    student_id = request.GET.get('student', '').strip()
    rating = request.GET.get('rating', '').strip()

    feedbacks = Feedback.objects.select_related(
        'student', 'resource', 'resource__subject'
    )
    if query:
        feedbacks = feedbacks.filter(
            Q(student__name__icontains=query)
            | Q(resource__title__icontains=query)
            | Q(comment__icontains=query)
        )
    if student_id.isdigit():
        feedbacks = feedbacks.filter(student_id=student_id)
    if rating.isdigit():
        feedbacks = feedbacks.filter(rating=int(rating))

    feedbacks = feedbacks.order_by('-created_at')

    paginator = Paginator(feedbacks, 10)
    page = paginator.get_page(request.GET.get('page', 1))

    context = {
        'feedbacks': page,
        'students': Student.objects.order_by('name'),
        'resources': StudyResource.objects.select_related('subject').order_by('title'),
        'rating_choices': RATING_CHOICES,
        'query': query,
        'selected_student': student_id,
        'selected_rating': rating,
    }
    return render(request, 'feedback/list.html', context)


@login_required(login_url='login')
@require_POST
def feedback_save_ajax(request):
    feedback_id = request.POST.get('id')
    feedback = (
        get_object_or_404(Feedback, pk=feedback_id)
        if feedback_id
        else Feedback()
    )
    is_update = bool(feedback_id)

    student_id = request.POST.get('student', '').strip()
    resource_id = request.POST.get('resource', '').strip()
    rating = request.POST.get('rating', '').strip()
    comment = request.POST.get('comment', '').strip()

    if not student_id.isdigit():
        return JsonResponse({'error': 'Please choose a student.'}, status=400)
    if not resource_id.isdigit():
        return JsonResponse({'error': 'Please choose a resource.'}, status=400)

    student = Student.objects.filter(pk=student_id).first()
    if student is None:
        return JsonResponse({'error': 'That student no longer exists.'}, status=400)
    resource = StudyResource.objects.filter(pk=resource_id).first()
    if resource is None:
        return JsonResponse({'error': 'That resource no longer exists.'}, status=400)

    try:
        rating = int(rating)
    except ValueError:
        return JsonResponse({'error': 'Rating is required.'}, status=400)
    if rating not in RATING_CHOICES:
        return JsonResponse(
            {'error': 'Rating must be between 1 and 5.'}, status=400
        )

    feedback.student = student
    feedback.resource = resource
    feedback.rating = rating
    feedback.comment = comment or None
    feedback.save()

    messages.success(
        request,
        f'Feedback for "{resource.title}" has been '
        f'{"updated" if is_update else "saved"} successfully.',
    )
    return JsonResponse({'status': 'success', 'id': feedback.pk})


@login_required(login_url='login')
@require_POST
def feedback_delete_ajax(request, pk):
    feedback = get_object_or_404(Feedback, pk=pk)
    feedback.delete()
    messages.success(request, 'Feedback has been deleted.')
    return JsonResponse({'status': 'deleted'})
