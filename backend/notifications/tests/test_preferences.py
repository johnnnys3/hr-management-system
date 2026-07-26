from django.test import TestCase
from rest_framework.test import APIClient

from iam.roles import HR_OFFICER

from .helpers import user_with_role


class NotificationPreferenceTests(TestCase):
    def setUp(self):
        self.user = user_with_role('a@example.com', HR_OFFICER)
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_get_creates_default_preference_for_a_user_with_none(self):
        response = self.client.get('/api/notification-preferences/me/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['email_enabled'], True)
        self.assertEqual(response.data['sms_enabled'], False)

    def test_patch_updates_own_preference(self):
        response = self.client.patch(
            '/api/notification-preferences/me/', {'sms_enabled': True}, format='json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['sms_enabled'], True)
        self.user.notification_preference.refresh_from_db()
        self.assertTrue(self.user.notification_preference.sms_enabled)

    def test_anonymous_cannot_access(self):
        anon_client = APIClient()
        response = anon_client.get('/api/notification-preferences/me/')
        self.assertEqual(response.status_code, 401)
