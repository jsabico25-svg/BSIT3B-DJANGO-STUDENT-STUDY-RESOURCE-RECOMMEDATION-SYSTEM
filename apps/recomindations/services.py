from decimal import Decimal

from django.db.models import Avg

from apps.feedback.models import Feedback
from apps.students.models import Student
from apps.study_resources.models import StudyResource

from .models import Recommendation

SKILL_ORDER = {'Beginner': 0, 'Intermediate': 1, 'Advanced': 2}
NEUTRAL_BASE = 60.0


def calculate_score(avg_rating, skill_level, difficulty_level):
    base = (float(avg_rating) if avg_rating is not None else 3.0) * 20

    adjustment = 0
    if difficulty_level in SKILL_ORDER:
        gap = abs(
            SKILL_ORDER.get(skill_level, 0) - SKILL_ORDER[difficulty_level]
        )
        adjustment = {0: 10, 1: -5}.get(gap, -15)

    score = max(0.0, min(100.0, base + adjustment))
    return Decimal(str(score)).quantize(Decimal('0.01'))


def generate_for_student(student):
    enrollments = list(
        student.student_subjects.values_list('subject_id', 'skill_level')
    )
    if not enrollments:
        return 0

    skill_by_subject = dict(enrollments)
    subject_ids = list(skill_by_subject)

    rated_resource_ids = Feedback.objects.filter(student=student).values_list(
        'resource_id', flat=True
    )
    rated_resource_ids = list(rated_resource_ids)

    Recommendation.objects.filter(
        student=student,
        resource__subject_id__in=subject_ids,
        resource_id__in=rated_resource_ids,
    ).delete()

    candidates = (
        StudyResource.objects.filter(subject_id__in=subject_ids)
        .exclude(resource_id__in=rated_resource_ids)
        .annotate(avg_rating=Avg('feedbacks__rating'))
    )

    generated = 0
    for resource in candidates:
        score = calculate_score(
            resource.avg_rating,
            skill_by_subject.get(resource.subject_id, 'Beginner'),
            resource.difficulty_level,
        )
        Recommendation.objects.update_or_create(
            student=student,
            resource=resource,
            defaults={'score': score},
        )
        generated += 1

    return generated


def generate_for_all_students():
    total = 0
    students = Student.objects.filter(student_subjects__isnull=False).distinct()
    for student in students:
        total += generate_for_student(student)
    return total
