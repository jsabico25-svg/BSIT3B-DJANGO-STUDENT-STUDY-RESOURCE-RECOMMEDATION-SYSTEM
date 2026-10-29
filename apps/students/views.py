from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.core.validators import validate_email
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

from .models import Student

MAX_NAME_LENGTH = 100
MAX_COURSE_LENGTH = 100
MIN_PASSWORD_LENGTH = 8
YEAR_LEVELS = range(1, 7)


@login_required(login_url='login')
def student_list_page(request):
    query = request.GET.get('q', '').strip()
    students = Student.objects.annotate(
        enrollment_count=Count('student_subjects', distinct=True),
        feedback_count=Count('feedbacks', distinct=True),
    ).order_by('name')
    if query:
        students = students.filter(
            Q(name__icontains=query)
            | Q(email__icontains=query)
            | Q(course__icontains=query)
        )
    paginator = Paginator(students, 10)
    page = paginator.get_page(request.GET.get('page', 1))
    return render(
        request,
        'students/list.html',
        {'students': page, 'query': query},
    )


@login_required(login_url='login')
@require_POST
def student_save_ajax(request):
    student_id = request.POST.get('id')
    student = (
        get_object_or_404(Student, pk=student_id) if student_id else Student()
    )
    is_update = bool(student_id)

    name = request.POST.get('name', '').strip()
    email = request.POST.get('email', '').strip().lower()
    password = request.POST.get('password', '')
    course = request.POST.get('course', '').strip()
    year_level = request.POST.get('year_level', '').strip()

    if not name:
        return JsonResponse({'error': 'Name is required.'}, status=400)
    if len(name) > MAX_NAME_LENGTH:
        return JsonResponse(
            {'error': f'Name must be {MAX_NAME_LENGTH} characters or fewer.'},
            status=400,
        )
    if not email:
        return JsonResponse({'error': 'Email is required.'}, status=400)
    try:
        validate_email(email)
    except ValidationError:
        return JsonResponse({'error': 'Enter a valid email address.'}, status=400)
    if len(course) > MAX_COURSE_LENGTH:
        return JsonResponse(
            {'error': f'Course must be {MAX_COURSE_LENGTH} characters or fewer.'},
            status=400,
        )

    if year_level:
        try:
            year_level = int(year_level)
        except ValueError:
            return JsonResponse({'error': 'Year level must be a number.'}, status=400)
        if year_level not in YEAR_LEVELS:
            return JsonResponse(
                {'error': 'Year level must be between 1 and 6.'}, status=400
            )
    else:
        year_level = None

    if not is_update and not password:
        return JsonResponse({'error': 'Password is required.'}, status=400)
    if password and len(password) < MIN_PASSWORD_LENGTH:
        return JsonResponse(
            {'error': f'Password must be at least {MIN_PASSWORD_LENGTH} characters.'},
            status=400,
        )

    duplicates = Student.objects.filter(email__iexact=email)
    if student.pk:
        duplicates = duplicates.exclude(pk=student.pk)
    if duplicates.exists():
        return JsonResponse(
            {'error': 'That email address is already in use.'}, status=400
        )

    student.name = name
    student.email = email
    student.course = course or None
    student.year_level = year_level
    if password:
        student.password = make_password(password)
    student.save()

    messages.success(
        request,
        f'Student "{student.name}" has been '
        f'{"updated" if is_update else "saved"} successfully.',
    )
    return JsonResponse({'status': 'success', 'id': student.pk})


@login_required(login_url='login')
@require_POST
def student_delete_ajax(request, pk):
    student = get_object_or_404(Student, pk=pk)
    name = student.name
    student.delete()
    messages.success(
        request,
        f'Student "{name}" and their enrollments, feedback and '
        'recommendations have been deleted.',
    )
    return JsonResponse({'status': 'deleted'})
