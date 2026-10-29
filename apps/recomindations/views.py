from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

from apps.students.models import Student
from apps.study_resources.models import StudyResource

from .models import Recommendation
from .services import generate_for_all_students, generate_for_student


@login_required(login_url='login')
def recommendation_list_page(request):
    query = request.GET.get('q', '').strip()
    student_id = request.GET.get('student', '').strip()

    recommendations = Recommendation.objects.select_related(
        'student', 'resource', 'resource__subject'
    )
    if query:
        recommendations = recommendations.filter(
            Q(student__name__icontains=query)
            | Q(resource__title__icontains=query)
            | Q(resource__subject__subject_name__icontains=query)
        )
    if student_id.isdigit():
        recommendations = recommendations.filter(student_id=student_id)

    recommendations = recommendations.order_by('student__name', '-score')

    paginator = Paginator(recommendations, 10)
    page = paginator.get_page(request.GET.get('page', 1))

    context = {
        'recommendations': page,
        'students': Student.objects.order_by('name'),
        'resources': StudyResource.objects.select_related('subject').order_by('title'),
        'query': query,
        'selected_student': student_id,
    }
    return render(request, 'recommendations/list.html', context)


@login_required(login_url='login')
@require_POST
def recommendation_save_ajax(request):
    recommendation_id = request.POST.get('id')
    recommendation = (
        get_object_or_404(Recommendation, pk=recommendation_id)
        if recommendation_id
        else Recommendation()
    )
    is_update = bool(recommendation_id)

    student_id = request.POST.get('student', '').strip()
    resource_id = request.POST.get('resource', '').strip()
    score = request.POST.get('score', '').strip()

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

    if score:
        try:
            score = Decimal(score)
        except InvalidOperation:
            return JsonResponse({'error': 'Score must be a number.'}, status=400)
        if score < 0 or score > 100:
            return JsonResponse(
                {'error': 'Score must be between 0 and 100.'}, status=400
            )
    else:
        score = Decimal('0.00')

    duplicates = Recommendation.objects.filter(
        student=student, resource=resource
    )
    if recommendation.pk:
        duplicates = duplicates.exclude(pk=recommendation.pk)
    if duplicates.exists():
        return JsonResponse(
            {'error': 'That resource is already recommended to this student.'},
            status=400,
        )

    recommendation.student = student
    recommendation.resource = resource
    recommendation.score = score
    recommendation.save()

    messages.success(
        request,
        f'Recommendation for "{student.name}" has been '
        f'{"updated" if is_update else "saved"} successfully.',
    )
    return JsonResponse({'status': 'success', 'id': recommendation.pk})


@login_required(login_url='login')
@require_POST
def recommendation_delete_ajax(request, pk):
    recommendation = get_object_or_404(Recommendation, pk=pk)
    recommendation.delete()
    messages.success(request, 'Recommendation has been deleted.')
    return JsonResponse({'status': 'deleted'})


@login_required(login_url='login')
@require_POST
def recommendation_generate_ajax(request, student_pk):
    student = get_object_or_404(Student, pk=student_pk)
    generated = generate_for_student(student)
    if generated:
        messages.success(
            request,
            f'Generated {generated} recommendation'
            f'{"" if generated == 1 else "s"} for {student.name}.',
        )
    else:
        messages.info(
            request,
            f'No new recommendations for {student.name}. Enroll them in '
            'subjects with unrated resources first.',
        )
    return JsonResponse({'status': 'success', 'generated': generated})


@login_required(login_url='login')
@require_POST
def recommendation_generate_all_ajax(request):
    generated = generate_for_all_students()
    if generated:
        messages.success(
            request,
            f'Generated {generated} recommendation'
            f'{"" if generated == 1 else "s"} for all enrolled students.',
        )
    else:
        messages.info(
            request,
            'No recommendations were generated. Check enrollments and '
            'available unrated resources.',
        )
    return JsonResponse({'status': 'success', 'generated': generated})
