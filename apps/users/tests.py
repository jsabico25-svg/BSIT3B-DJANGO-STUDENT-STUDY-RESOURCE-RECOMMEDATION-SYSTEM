from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class UserAccessTests(TestCase):
    def setUp(self):
        self.url = reverse('users:user_list')

    def test_anonymous_user_is_sent_to_login(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")

    def test_regular_user_is_redirected_with_message(self):
        user = User.objects.create_user(username='instructor', password='pass12345')
        self.client.force_login(user)

        response = self.client.get(self.url, follow=True)

        self.assertRedirects(response, reverse('dashboard'))
        messages = [str(m) for m in response.context['messages']]
        self.assertIn(
            'The Users page is only available to administrators.', messages
        )

    def test_superuser_can_open_users_page(self):
        admin = User.objects.create_superuser(
            username='admin', email='admin@example.com', password='pass12345'
        )
        self.client.force_login(admin)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
