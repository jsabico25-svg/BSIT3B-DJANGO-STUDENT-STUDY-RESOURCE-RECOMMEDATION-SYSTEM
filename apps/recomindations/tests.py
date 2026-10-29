from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.feedback.models import Feedback
from apps.student_subjects.models import StudentSubject
from apps.students.models import Student
from apps.study_resources.models import StudyResource
from apps.subject.models import Subject

from .models import Recommendation
from .services import calculate_score, generate_for_student

User = get_user_model()


class CalculateScoreTests(TestCase):
    def test_unrated_matching_difficulty(self):
        self.assertEqual(calculate_score(None, 'Beginner', 'Beginner'), Decimal('70.00'))

    def test_high_rating_penalised_by_far_difficulty(self):
        self.assertEqual(calculate_score(5, 'Beginner', 'Advanced'), Decimal('85.00'))

    def test_low_rating_penalised_by_far_difficulty(self):
        self.assertEqual(calculate_score(1, 'Advanced', 'Beginner'), Decimal('5.00'))

    def test_score_never_exceeds_hundred(self):
        self.assertEqual(calculate_score(5, 'Advanced', 'Advanced'), Decimal('100.00'))


class GenerateRecommendationTests(TestCase):
    def setUp(self):
        self.student = Student.objects.create(
            name='Maria Santos',
            email='maria@example.com',
            password='x',
        )
        self.other_student = Student.objects.create(
            name='Jose Cruz',
            email='jose@example.com',
            password='x',
        )
        self.ds = Subject.objects.create(subject_name='Data Structures')
        self.math = Subject.objects.create(subject_name='Mathematics')
        self.enrolled_resource = StudyResource.objects.create(
            subject=self.ds,
            title='Big-O Cheat Sheet',
            difficulty_level='Beginner',
        )
        self.rated_resource = StudyResource.objects.create(
            subject=self.ds,
            title='Sorting Visualiser',
            difficulty_level='Beginner',
        )
        self.other_subject_resource = StudyResource.objects.create(
            subject=self.math,
            title='Calculus Primer',
            difficulty_level='Beginner',
        )
        StudentSubject.objects.create(student=self.student, subject=self.ds)
        Feedback.objects.create(
            student=self.student,
            resource=self.rated_resource,
            rating=4,
        )

    def test_only_enrolled_subjects_and_unrated_resources(self):
        generated = generate_for_student(self.student)

        self.assertEqual(generated, 1)
        recommended = Recommendation.objects.filter(student=self.student)
        self.assertEqual(
            list(recommended.values_list('resource__title', flat=True)),
            ['Big-O Cheat Sheet'],
        )
        self.assertFalse(
            Recommendation.objects.filter(
                student=self.student, resource=self.other_subject_resource
            ).exists()
        )
        self.assertFalse(
            Recommendation.objects.filter(
                student=self.student, resource=self.rated_resource
            ).exists()
        )

    def test_regenerate_updates_instead_of_duplicating(self):
        generate_for_student(self.student)
        Feedback.objects.create(
            student=self.other_student,
            resource=self.enrolled_resource,
            rating=4,
        )

        generate_for_student(self.student)

        self.assertEqual(
            Recommendation.objects.filter(student=self.student).count(), 1
        )
        recommendation = Recommendation.objects.get(student=self.student)
        self.assertEqual(recommendation.score, Decimal('90.00'))

    def test_rated_resource_recommendation_is_removed(self):
        generate_for_student(self.student)
        Feedback.objects.create(
            student=self.student,
            resource=self.enrolled_resource,
            rating=5,
        )

        generated = generate_for_student(self.student)

        self.assertEqual(generated, 0)
        self.assertFalse(
            Recommendation.objects.filter(student=self.student).exists()
        )

    def test_student_without_enrollments_gets_nothing(self):
        self.assertEqual(generate_for_student(self.other_student), 0)
        self.assertFalse(
            Recommendation.objects.filter(student=self.other_student).exists()
        )


class RecommendationViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='staff', password='staffpass123'
        )
        self.client.force_login(self.user)
        self.student = Student.objects.create(
            name='Maria Santos', email='maria@example.com', password='x'
        )
        self.subject = Subject.objects.create(subject_name='Data Structures')
        self.resource = StudyResource.objects.create(
            subject=self.subject,
            title='Big-O Cheat Sheet',
            difficulty_level='Beginner',
        )
        StudentSubject.objects.create(
            student=self.student,
            subject=self.subject,
            skill_level='Beginner',
        )

    def test_generate_endpoint_creates_recommendation(self):
        response = self.client.post(
            reverse(
                'recomindations:recommendation_generate_ajax',
                args=[self.student.pk],
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['generated'], 1)
        recommendation = Recommendation.objects.get()
        self.assertEqual(recommendation.score, Decimal('70.00'))

    def test_manual_save_rejects_duplicate(self):
        Recommendation.objects.create(
            student=self.student, resource=self.resource, score=50
        )

        response = self.client.post(
            reverse('recomindations:recommendation_save_ajax'),
            {
                'student': self.student.pk,
                'resource': self.resource.pk,
                'score': '80',
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Recommendation.objects.count(), 1)

    def test_manual_score_out_of_range_is_rejected(self):
        response = self.client.post(
            reverse('recomindations:recommendation_save_ajax'),
            {
                'student': self.student.pk,
                'resource': self.resource.pk,
                'score': '150',
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(Recommendation.objects.exists())
