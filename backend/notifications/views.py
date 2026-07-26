from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Notification, NotificationPreference
from .serializers import NotificationPreferenceSerializer, NotificationSerializer


class NotificationListView(ListAPIView):
    """`GET /api/notifications/`, `docs/06-api-contracts.md` §4.8. Own feed
    only — every authenticated user, any role, reaches this endpoint over
    their own rows: no permission-matrix cell applies.
    """

    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Notification.objects.filter(recipient=self.request.user)
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
        read_at_isnull = self.request.query_params.get('read_at__isnull')
        if read_at_isnull is not None:
            queryset = queryset.filter(read_at__isnull=read_at_isnull.lower() == 'true')
        return queryset


class NotificationMarkReadView(APIView):
    """`POST /api/notifications/{id}/read/`, `docs/06-api-contracts.md` §4.8.
    Another user's `id` 404s from the scoping below, not a 403.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
        # Conditional UPDATE, not read-then-save: two concurrent POSTs must
        # not let the second overwrite the first's `read_at` with its own.
        Notification.objects.filter(pk=notification.pk, read_at__isnull=True).update(read_at=timezone.now())
        notification.refresh_from_db()
        return Response(NotificationSerializer(notification).data)


class NotificationPreferenceView(APIView):
    """`GET/PATCH /api/notification-preferences/me/`. Self only, per
    docs/superpowers/specs/2026-07-26-notifications-email-sms-design.md §5.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        preference, _ = NotificationPreference.objects.get_or_create(user=request.user)
        return Response(NotificationPreferenceSerializer(preference).data)

    def patch(self, request):
        preference, _ = NotificationPreference.objects.get_or_create(user=request.user)
        serializer = NotificationPreferenceSerializer(preference, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
