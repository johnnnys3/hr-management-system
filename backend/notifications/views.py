from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Notification
from .serializers import NotificationSerializer


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
        if notification.read_at is None:
            notification.read_at = timezone.now()
            notification.save(update_fields=['read_at'])
        return Response(NotificationSerializer(notification).data)
