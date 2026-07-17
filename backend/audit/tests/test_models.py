from django.contrib.auth import get_user_model
from django.test import TestCase

from audit import services
from audit.models import AuditLog

User = get_user_model()


class AuditLogWriterTests(TestCase):
    def test_record_writes_an_entry(self):
        user = User.objects.create_user(username='alice', password='irrelevant')

        entry = services.record(
            category=AuditLog.CATEGORY_LOGIN_ATTEMPT,
            action='login_success',
            actor=user,
            detail={'ip': '127.0.0.1'},
        )

        self.assertEqual(AuditLog.objects.count(), 1)
        self.assertEqual(entry.actor, user)
        self.assertEqual(entry.category, AuditLog.CATEGORY_LOGIN_ATTEMPT)
        self.assertEqual(entry.action, 'login_success')
        self.assertEqual(entry.detail, {'ip': '127.0.0.1'})
        self.assertIsNotNone(entry.occurred_at)

    def test_record_allows_no_actor(self):
        """A failed login against a non-existent account has no actor."""
        entry = services.record(category=AuditLog.CATEGORY_LOGIN_ATTEMPT, action='login_failed')

        self.assertIsNone(entry.actor)

    def test_actor_deletion_nulls_the_reference_rather_than_removing_the_entry(self):
        user = User.objects.create_user(username='bob', password='irrelevant')
        entry = services.record(category=AuditLog.CATEGORY_PERMISSION_CHANGE, action='role_granted', actor=user)

        user.delete()
        entry.refresh_from_db()

        self.assertIsNone(entry.actor_id)
        self.assertEqual(AuditLog.objects.count(), 1)

    def test_no_update_or_delete_path_is_exposed_by_the_manager(self):
        """The application layer offers no way to mutate an entry — only `record()` (create)."""
        self.assertEqual(sorted(vars(services).keys() & {'record', 'update', 'delete'}), ['record'])
