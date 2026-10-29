from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.students.models import Student
from apps.student_subjects.models import StudentSubject
from apps.subject.models import Subject

User = get_user_model()


class EnrollmentViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='staff', password='staffpass123'
        )
        self.client.force_login(self.user)
        self.student = Student.objects.create(
            name='Maria Santos', email='maria@example.com', password='x'
        )
        self.subject = Subject.objects.create(subject_name='Data Structures')
        self.url = reverse('student_subjects:enrollment_save_ajax')

    def test_create_enrollment(self):
        response = self.client.post(self.url, {
            'student': self.student.pk,
            'subject': self.subject.pk,
            'skill_level': 'Intermediate',
        })

        self.assertEqual(response.status_code, 200)
        enrollment = StudentSubject.objects.get()
        self.assertEqual(enrollment.skill_level, 'Intermediate')

    def test_duplicate_enrollment_is_rejected(self):
        StudentSubject.objects.create(
            student=self.student, subject=self.subject
        )

        response = self.client.post(self.url, {
            'student': self.student.pk,
            'subject': self.subject.pk,
        })

        self.assertEqual(response.status_code, 400)
        self.assertIn('already enrolled', response.json()['error'])
        self.assertEqual(StudentSubject.objects.count(), 1)

    def test_invalid_skill_level_is_rejected(self):
        response = self.client.post(self.url, {
            'student': self.student.pk,
            'subject': self.subject.pk,
            'skill_level': 'Expert',
        })

        self.assertEqual(response.status_code, 400)
        self.assertFalse(StudentSubject.objects.exists())

    def test_update_own_enrollment_is_allowed(self):
        enrollment = StudentSubject.objects.create(
            student=self.student, subject=self.subject
        )

        response = self.client.post(self.url, {
            'id': enrollment.pk,
            'student': self.student.pk,
            'subject': self.subject.pk,
            'skill_level': 'Advanced',
        })

        self.assertEqual(response.status_code, 200)
        enrollment.refresh_from_db()
        self.assertEqual(enrollment.skill_level, 'Advanced')
