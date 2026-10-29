from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.subject.models import Subject

from .models import StudyResource

User = get_user_model()


class ResourceViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='staff', password='staffpass123'
        )
        self.client.force_login(self.user)
        self.subject = Subject.objects.create(subject_name='Data Structures')
        self.url = reverse('study_resources:resource_save_ajax')

    def test_create_resource(self):
        response = self.client.post(self.url, {
            'subject': self.subject.pk,
            'title': 'Big-O Cheat Sheet',
            'resource_type': 'Article',
            'resource_url': 'https://www.bigocheatsheet.com/',
            'difficulty_level': 'Beginner',
        })

        self.assertEqual(response.status_code, 200)
        resource = StudyResource.objects.get()
        self.assertEqual(resource.subject, self.subject)
        self.assertEqual(resource.difficulty_level, 'Beginner')

    def test_subject_is_required(self):
        response = self.client.post(self.url, {'title': 'No subject'})

        self.assertEqual(response.status_code, 400)
        self.assertFalse(StudyResource.objects.exists())

    def test_invalid_url_is_rejected(self):
        response = self.client.post(self.url, {
            'subject': self.subject.pk,
            'title': 'Bad link',
            'resource_url': 'not-a-url',
        })

        self.assertEqual(response.status_code, 400)
        self.assertFalse(StudyResource.objects.exists())

    def test_invalid_difficulty_is_rejected(self):
        response = self.client.post(self.url, {
            'subject': self.subject.pk,
            'title': 'Bad level',
            'difficulty_level': 'Expert',
        })

        self.assertEqual(response.status_code, 400)
        self.assertFalse(StudyResource.objects.exists())
