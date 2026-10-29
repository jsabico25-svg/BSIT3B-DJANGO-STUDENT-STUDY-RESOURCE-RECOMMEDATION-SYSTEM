from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.test import TestCase
from django.urls import reverse

from .models import Student

User = get_user_model()


class StudentViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='staff', password='staffpass123'
        )
        self.client.force_login(self.user)
        self.url = reverse('students:student_save_ajax')

    def test_create_hashes_password(self):
        response = self.client.post(self.url, {
            'name': 'Maria Santos',
            'email': 'maria@example.com',
            'password': 'secret123',
            'course': 'BSIT',
            'year_level': '3',
        })

        self.assertEqual(response.status_code, 200)
        student = Student.objects.get(email='maria@example.com')
        self.assertNotEqual(student.password, 'secret123')
        self.assertTrue(check_password('secret123', student.password))
        self.assertEqual(student.year_level, 3)

    def test_duplicate_email_is_rejected_case_insensitively(self):
        Student.objects.create(
            name='Existing', email='maria@example.com', password='x'
        )

        response = self.client.post(self.url, {
            'name': 'Maria Santos',
            'email': 'MARIA@example.com',
            'password': 'secret123',
        })

        self.assertEqual(response.status_code, 400)
        self.assertIn('already in use', response.json()['error'])
        self.assertEqual(Student.objects.count(), 1)

    def test_short_password_is_rejected(self):
        response = self.client.post(self.url, {
            'name': 'Maria Santos',
            'email': 'maria@example.com',
            'password': 'short',
        })

        self.assertEqual(response.status_code, 400)
        self.assertFalse(Student.objects.exists())

    def test_invalid_year_level_is_rejected(self):
        response = self.client.post(self.url, {
            'name': 'Maria Santos',
            'email': 'maria@example.com',
            'password': 'secret123',
            'year_level': '7',
        })

        self.assertEqual(response.status_code, 400)
        self.assertFalse(Student.objects.exists())

    def test_update_without_password_keeps_hash(self):
        student = Student.objects.create(
            name='Maria Santos',
            email='maria@example.com',
            password='keep-me',
        )

        response = self.client.post(self.url, {
            'id': student.pk,
            'name': 'Maria S. Santos',
            'email': 'maria@example.com',
            'password': '',
        })

        self.assertEqual(response.status_code, 200)
        student.refresh_from_db()
        self.assertEqual(student.name, 'Maria S. Santos')
        self.assertEqual(student.password, 'keep-me')

    def test_anonymous_user_is_redirected_to_login(self):
        self.client.logout()
        response = self.client.get(reverse('students:student_list'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/?next=', response.url)


class ModuleAccessTests(TestCase):
    def test_all_module_pages_require_login(self):
        for name in [
            'subject:subject_list',
            'study_resources:resource_list',
            'students:student_list',
            'student_subjects:enrollment_list',
            'feedback:feedback_list',
            'recomindations:recommendation_list',
        ]:
            with self.subTest(name=name):
                response = self.client.get(reverse(name))
                self.assertEqual(response.status_code, 302)
                self.assertIn('/?next=', response.url)
