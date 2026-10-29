from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.students.models import Student
from apps.study_resources.models import StudyResource
from apps.subject.models import Subject

from .models import Feedback

User = get_user_model()


class FeedbackViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='staff', password='staffpass123'
        )
        self.client.force_login(self.user)
        self.student = Student.objects.create(
            name='Maria Santos', email='maria@example.com', password='x'
        )
        subject = Subject.objects.create(subject_name='Data Structures')
        self.resource = StudyResource.objects.create(
            subject=subject, title='Big-O Cheat Sheet'
        )
        self.url = reverse('feedback:feedback_save_ajax')

    def test_valid_rating_is_saved(self):
        response = self.client.post(self.url, {
            'student': self.student.pk,
            'resource': self.resource.pk,
            'rating': '5',
            'comment': 'Very useful.',
        })

        self.assertEqual(response.status_code, 200)
        feedback = Feedback.objects.get()
        self.assertEqual(feedback.rating, 5)

    def test_rating_above_five_is_rejected(self):
        response = self.client.post(self.url, {
            'student': self.student.pk,
            'resource': self.resource.pk,
            'rating': '6',
        })

        self.assertEqual(response.status_code, 400)
        self.assertFalse(Feedback.objects.exists())

    def test_rating_below_one_is_rejected(self):
        response = self.client.post(self.url, {
            'student': self.student.pk,
            'resource': self.resource.pk,
            'rating': '0',
        })

        self.assertEqual(response.status_code, 400)
        self.assertFalse(Feedback.objects.exists())
