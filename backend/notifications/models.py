from django.conf import settings
from django.db import models


class Notification(models.Model):
    """`notification`, `docs/05-database-schema.md` §3.2/§4.9. Visibility is
    a single equality (`recipient_user_id = current user`), not a queryset
    traversal — no visibility-rule matrix cell applies.
    """

    CATEGORY_PENDING_TASK = 'pending_task'
    CATEGORY_REQUEST_UPDATE = 'request_update'
    CATEGORY_CHOICES = [
        (CATEGORY_PENDING_TASK, 'Pending task'),
        (CATEGORY_REQUEST_UPDATE, 'Request update'),
    ]

    CHANNEL_IN_APP = 'in_app'
    CHANNEL_EMAIL = 'email'
    CHANNEL_BOTH = 'both'
    CHANNEL_CHOICES = [
        (CHANNEL_IN_APP, 'In-app'),
        (CHANNEL_EMAIL, 'Email'),
        (CHANNEL_BOTH, 'Both'),
    ]

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.RESTRICT, related_name='+', db_column='recipient_user_id',
    )
    category = models.CharField(max_length=32, choices=CATEGORY_CHOICES)
    channel = models.CharField(max_length=16, choices=CHANNEL_CHOICES)
    subject = models.TextField()
    body = models.TextField()
    related_type = models.CharField(max_length=100, null=True, blank=True)
    related_id = models.BigIntegerField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notification'
        ordering = ['-created_at']
