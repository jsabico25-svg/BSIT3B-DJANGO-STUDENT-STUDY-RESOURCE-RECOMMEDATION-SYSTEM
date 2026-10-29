from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Subject

User = get_user_model()


class SubjectViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='staff', password='staffpass123'
        )
        self.client.force_login(self.user)
        self.url = reverse('subject:subject_save_ajax')

    def test_create_subject(self):
        response = self.client.post(self.url, {
            'subject_name': 'Data Structures',
            'description': 'Core data structures',
        })

        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            Subject.objects.filter(subject_name='Data Structures').exists()
        )

    def test_duplicate_subject_name_is_rejected(self):
        Subject.objects.create(subject_name='Data Structures')

        response = self.client.post(self.url, {
            'subject_name': 'data structures',
        })

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Subject.objects.count(), 1)

    def test_blank_name_is_rejected(self):
        response = self.client.post(self.url, {'subject_name': '   '})

        self.assertEqual(response.status_code, 400)
        self.assertFalse(Subject.objects.exists())

    def test_delete_removes_subject(self):
        subject = Subject.objects.create(subject_name='Data Structures')

        response = self.client.post(
            reverse('subject:subject_delete_ajax', args=[subject.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Subject.objects.exists())
