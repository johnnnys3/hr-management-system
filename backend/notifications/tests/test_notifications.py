"""`/api/notifications/`, `docs/06-api-contracts.md` §4.8."""
from rest_framework.test import APITestCase

from iam.roles import HR_OFFICER
from notifications.models import Notification

from .helpers import user_with_role


class NotificationListTests(APITestCase):
    def setUp(self):
        self.user = user_with_role('me@example.com', HR_OFFICER)
        self.other_user = user_with_role('other@example.com', HR_OFFICER)

    def test_user_sees_only_own_notifications(self):
        Notification.objects.create(
            recipient=self.user, category=Notification.CATEGORY_PENDING_TASK, channel=Notification.CHANNEL_IN_APP,
            subject='Mine', body='Body',
        )
        Notification.objects.create(
            recipient=self.other_user, category=Notification.CATEGORY_PENDING_TASK,
            channel=Notification.CHANNEL_IN_APP, subject='Not mine', body='Body',
        )
        self.client.force_authenticate(self.user)

        response = self.client.get('/api/notifications/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['subject'], 'Mine')

    def test_filter_by_category(self):
        Notification.objects.create(
            recipient=self.user, category=Notification.CATEGORY_PENDING_TASK, channel=Notification.CHANNEL_IN_APP,
            subject='Task', body='Body',
        )
        Notification.objects.create(
            recipient=self.user, category=Notification.CATEGORY_REQUEST_UPDATE, channel=Notification.CHANNEL_IN_APP,
            subject='Update', body='Body',
        )
        self.client.force_authenticate(self.user)

        response = self.client.get('/api/notifications/?category=request_update')

        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['subject'], 'Update')

    def test_filter_by_read_at_isnull(self):
        unread = Notification.objects.create(
            recipient=self.user, category=Notification.CATEGORY_PENDING_TASK, channel=Notification.CHANNEL_IN_APP,
            subject='Unread', body='Body',
        )
        Notification.objects.create(
            recipient=self.user, category=Notification.CATEGORY_PENDING_TASK, channel=Notification.CHANNEL_IN_APP,
            subject='Read', body='Body', read_at='2026-07-01T00:00:00Z',
        )
        self.client.force_authenticate(self.user)

        response = self.client.get('/api/notifications/?read_at__isnull=true')

        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], unread.pk)

    def test_anonymous_user_cannot_list(self):
        response = self.client.get('/api/notifications/')

        self.assertEqual(response.status_code, 401)


class NotificationMarkReadTests(APITestCase):
    def setUp(self):
        self.user = user_with_role('me2@example.com', HR_OFFICER)
        self.other_user = user_with_role('other2@example.com', HR_OFFICER)
        self.notification = Notification.objects.create(
            recipient=self.user, category=Notification.CATEGORY_PENDING_TASK, channel=Notification.CHANNEL_IN_APP,
            subject='Mine', body='Body',
        )

    def test_user_can_mark_own_notification_read(self):
        self.client.force_authenticate(self.user)

        response = self.client.post(f'/api/notifications/{self.notification.pk}/read/')

        self.assertEqual(response.status_code, 200)
        self.notification.refresh_from_db()
        self.assertIsNotNone(self.notification.read_at)

    def test_marking_already_read_notification_is_idempotent(self):
        self.client.force_authenticate(self.user)
        self.client.post(f'/api/notifications/{self.notification.pk}/read/')
        self.notification.refresh_from_db()
        first_read_at = self.notification.read_at

        response = self.client.post(f'/api/notifications/{self.notification.pk}/read/')

        self.assertEqual(response.status_code, 200)
        self.notification.refresh_from_db()
        self.assertEqual(self.notification.read_at, first_read_at)

    def test_marking_another_users_notification_read_is_404(self):
        self.client.force_authenticate(self.other_user)

        response = self.client.post(f'/api/notifications/{self.notification.pk}/read/')

        self.assertEqual(response.status_code, 404)
