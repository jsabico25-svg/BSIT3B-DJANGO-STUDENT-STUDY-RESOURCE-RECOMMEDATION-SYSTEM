from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

from apps.students.models import Student
from apps.subject.models import Subject

from .models import StudentSubject

SKILL_LEVELS = ['Beginner', 'Intermediate', 'Advanced']


@login_required(login_url='login')
def enrollment_list_page(request):
    query = request.GET.get('q', '').strip()
    student_id = request.GET.get('student', '').strip()
    subject_id = request.GET.get('subject', '').strip()

    enrollments = StudentSubject.objects.select_related('student', 'subject')
    if query:
        enrollments = enrollments.filter(
            Q(student__name__icontains=query)
            | Q(subject__subject_name__icontains=query)
        )
    if student_id.isdigit():
        enrollments = enrollments.filter(student_id=student_id)
    if subject_id.isdigit():
        enrollments = enrollments.filter(subject_id=subject_id)

    enrollments = enrollments.order_by('student__name', 'subject__subject_name')

    paginator = Paginator(enrollments, 10)
    page = paginator.get_page(request.GET.get('page', 1))

    context = {
        'enrollments': page,
        'students': Student.objects.order_by('name'),
        'subjects': Subject.objects.order_by('subject_name'),
        'skill_levels': SKILL_LEVELS,
        'query': query,
        'selected_student': student_id,
        'selected_subject': subject_id,
    }
    return render(request, 'enrollments/list.html', context)


@login_required(login_url='login')
@require_POST
def enrollment_save_ajax(request):
    enrollment_id = request.POST.get('id')
    enrollment = (
        get_object_or_404(StudentSubject, pk=enrollment_id)
        if enrollment_id
        else StudentSubject()
    )
    is_update = bool(enrollment_id)

    student_id = request.POST.get('student', '').strip()
    subject_id = request.POST.get('subject', '').strip()
    skill_level = request.POST.get('skill_level', 'Beginner').strip()

    if not student_id.isdigit():
        return JsonResponse({'error': 'Please choose a student.'}, status=400)
    if not subject_id.isdigit():
        return JsonResponse({'error': 'Please choose a subject.'}, status=400)

    student = Student.objects.filter(pk=student_id).first()
    if student is None:
        return JsonResponse({'error': 'That student no longer exists.'}, status=400)
    subject = Subject.objects.filter(pk=subject_id).first()
    if subject is None:
        return JsonResponse({'error': 'That subject no longer exists.'}, status=400)

    if skill_level not in SKILL_LEVELS:
        return JsonResponse({'error': 'Invalid skill level.'}, status=400)

    duplicates = StudentSubject.objects.filter(
        student=student, subject=subject
    )
    if enrollment.pk:
        duplicates = duplicates.exclude(pk=enrollment.pk)
    if duplicates.exists():
        return JsonResponse(
            {'error': f'{student.name} is already enrolled in '
                      f'{subject.subject_name}.'},
            status=400,
        )

    enrollment.student = student
    enrollment.subject = subject
    enrollment.skill_level = skill_level
    enrollment.save()

    messages.success(
        request,
        f'{student.name} is {"updated" if is_update else "enrolled"} in '
        f'{subject.subject_name} ({skill_level}).',
    )
    return JsonResponse({'status': 'success', 'id': enrollment.pk})


@login_required(login_url='login')
@require_POST
def enrollment_delete_ajax(request, pk):
    enrollment = get_object_or_404(StudentSubject, pk=pk)
    label = str(enrollment)
    enrollment.delete()
    messages.success(request, f'Enrollment "{label}" has been deleted.')
    return JsonResponse({'status': 'deleted'})
