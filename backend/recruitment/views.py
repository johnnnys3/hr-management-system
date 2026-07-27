from django.core.files.base import ContentFile
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

import audit.services
import notifications.services
from audit.models import AuditLog
from notifications.models import Notification

from . import storage
from .models import Candidate, CandidateApplication, Interview, JobPosting, JobRequisition, OfferLetter
from .permissions import CanAccessJobRequisitions, CanDecideRequisition, CanWriteRecruitment
from .serializers import (
    CandidateApplicationSerializer,
    CandidateSerializer,
    InterviewSerializer,
    JobPostingSerializer,
    JobRequisitionSerializer,
    OfferDecisionSerializer,
    OfferLetterSerializer,
)

MAX_RESUME_SIZE_BYTES = 10 * 1024 * 1024


class JobRequisitionListCreateView(APIView):
    """`GET, POST /api/job-requisitions/`, `docs/06-api-contracts.md` §4.6."""

    permission_classes = [CanAccessJobRequisitions]

    def get(self, request):
        queryset = JobRequisition.objects.order_by('-created_at')
        status_filter = request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return Response(JobRequisitionSerializer(queryset, many=True).data)

    def post(self, request):
        serializer = JobRequisitionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            requisition = serializer.save(requested_by=request.user)
            audit.services.record(
                category=AuditLog.CATEGORY_RECORD_CHANGE,
                action='job_requisition_created',
                actor=request.user,
                target_type='job_requisition',
                target_id=requisition.pk,
            )
        return Response(JobRequisitionSerializer(requisition).data, status=status.HTTP_201_CREATED)


class JobRequisitionDetailView(APIView):
    """`PATCH /api/job-requisitions/{id}/`, `docs/06-api-contracts.md` §4.6."""

    permission_classes = [CanAccessJobRequisitions]

    def get(self, request, pk):
        requisition = get_object_or_404(JobRequisition, pk=pk)
        return Response(JobRequisitionSerializer(requisition).data)

    def patch(self, request, pk):
        requisition = get_object_or_404(JobRequisition, pk=pk)
        serializer = JobRequisitionSerializer(requisition, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            requisition = serializer.save()
            audit.services.record(
                category=AuditLog.CATEGORY_RECORD_CHANGE,
                action='job_requisition_updated',
                actor=request.user,
                target_type='job_requisition',
                target_id=requisition.pk,
            )
        return Response(JobRequisitionSerializer(requisition).data)


class JobRequisitionApproveView(APIView):
    """`POST /api/job-requisitions/{id}/approve/`, `docs/06-api-contracts.md`
    §4.6. A dedicated action endpoint, not a `PATCH` to `status`, per §2.9 —
    the transition also writes `approved_by` and an audit entry.

    ADR-0013: HR Administrator now both creates and approves requisitions
    (Recruiter, the prior role that only created them, is retired), so a
    requisition's creator can no longer be assumed to differ from its
    approver. Rejected `403` with `code: "self_approval_forbidden"` where
    the caller is the requisition's `requested_by` — checked first, before
    the general permission and status checks, mirroring
    `PayrollRunApproveView` and its `job_requisition_approver_not_requester`
    database counterpart, `docs/05-database-schema.md` §4.7."""

    permission_classes = [CanDecideRequisition]

    def post(self, request, pk):
        with transaction.atomic():
            requisition = get_object_or_404(JobRequisition.objects.select_for_update(), pk=pk)
            if request.user.pk == requisition.requested_by_id:
                return Response(
                    {'code': 'self_approval_forbidden', 'detail': 'the requester of a job requisition cannot approve it.'},
                    status=status.HTTP_403_FORBIDDEN,
                )
            if requisition.status not in (JobRequisition.STATUS_DRAFT, JobRequisition.STATUS_PENDING_APPROVAL):
                return Response(
                    {'detail': f'requisition cannot be approved from status {requisition.status!r}.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            requisition.status = JobRequisition.STATUS_APPROVED
            requisition.approved_by = request.user
            requisition.save(update_fields=['status', 'approved_by', 'updated_at'])
            audit.services.record(
                category=AuditLog.CATEGORY_RECORD_CHANGE,
                action='job_requisition_approved',
                actor=request.user,
                target_type='job_requisition',
                target_id=requisition.pk,
            )
            notifications.services.send(
                recipient=requisition.requested_by,
                category=Notification.CATEGORY_REQUEST_UPDATE,
                channel=Notification.CHANNEL_IN_APP,
                subject='Job requisition approved',
                body=f'Your job requisition #{requisition.pk} has been approved.',
                related_type='job_requisition',
                related_id=requisition.pk,
            )
        return Response(JobRequisitionSerializer(requisition).data)


class JobRequisitionRejectView(APIView):
    """`POST /api/job-requisitions/{id}/reject/`, `docs/06-api-contracts.md` §4.6."""

    permission_classes = [CanDecideRequisition]

    def post(self, request, pk):
        with transaction.atomic():
            requisition = get_object_or_404(JobRequisition.objects.select_for_update(), pk=pk)
            if requisition.status not in (JobRequisition.STATUS_DRAFT, JobRequisition.STATUS_PENDING_APPROVAL):
                return Response(
                    {'detail': f'requisition cannot be rejected from status {requisition.status!r}.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            requisition.status = JobRequisition.STATUS_REJECTED
            requisition.save(update_fields=['status', 'updated_at'])
            audit.services.record(
                category=AuditLog.CATEGORY_RECORD_CHANGE,
                action='job_requisition_rejected',
                actor=request.user,
                target_type='job_requisition',
                target_id=requisition.pk,
            )
            notifications.services.send(
                recipient=requisition.requested_by,
                category=Notification.CATEGORY_REQUEST_UPDATE,
                channel=Notification.CHANNEL_IN_APP,
                subject='Job requisition rejected',
                body=f'Your job requisition #{requisition.pk} has been rejected.',
                related_type='job_requisition',
                related_id=requisition.pk,
            )
        return Response(JobRequisitionSerializer(requisition).data)


class JobPostingListCreateView(APIView):
    """`GET, POST, PATCH /api/job-postings/`, `docs/06-api-contracts.md`
    §4.6. `POST` requires `requisition.status = 'approved'` — enforced here,
    not a schema constraint (`docs/05-database-schema.md` §4.7)."""

    permission_classes = [CanWriteRecruitment]

    def get(self, request):
        queryset = JobPosting.objects.order_by('-created_at')
        requisition_id = request.query_params.get('requisition_id')
        if requisition_id:
            queryset = queryset.filter(requisition_id=requisition_id)
        return Response(JobPostingSerializer(queryset, many=True).data)

    def post(self, request):
        serializer = JobPostingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        requisition = serializer.validated_data['requisition']
        if requisition.status != JobRequisition.STATUS_APPROVED:
            return Response(
                {'detail': 'requisition must be approved before a posting can be created.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        with transaction.atomic():
            posting = serializer.save()
            audit.services.record(
                category=AuditLog.CATEGORY_RECORD_CHANGE,
                action='job_posting_created',
                actor=request.user,
                target_type='job_posting',
                target_id=posting.pk,
            )
        return Response(JobPostingSerializer(posting).data, status=status.HTTP_201_CREATED)


class JobPostingDetailView(APIView):
    """`PATCH /api/job-postings/{id}/`, `docs/06-api-contracts.md` §4.6."""

    permission_classes = [CanWriteRecruitment]

    def get(self, request, pk):
        posting = get_object_or_404(JobPosting, pk=pk)
        return Response(JobPostingSerializer(posting).data)

    def patch(self, request, pk):
        posting = get_object_or_404(JobPosting, pk=pk)
        serializer = JobPostingSerializer(posting, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            posting = serializer.save()
            audit.services.record(
                category=AuditLog.CATEGORY_RECORD_CHANGE,
                action='job_posting_updated',
                actor=request.user,
                target_type='job_posting',
                target_id=posting.pk,
            )
        return Response(JobPostingSerializer(posting).data)


class JobPostingPublishView(APIView):
    """`POST /api/job-postings/{id}/publish/`, `docs/06-api-contracts.md` §4.6."""

    permission_classes = [CanWriteRecruitment]

    def post(self, request, pk):
        with transaction.atomic():
            posting = get_object_or_404(JobPosting.objects.select_for_update(), pk=pk)
            if posting.published_at is not None:
                return Response({'detail': 'posting is already published.'}, status=status.HTTP_400_BAD_REQUEST)
            posting.published_at = timezone.now()
            posting.save(update_fields=['published_at', 'updated_at'])
            audit.services.record(
                category=AuditLog.CATEGORY_RECORD_CHANGE,
                action='job_posting_published',
                actor=request.user,
                target_type='job_posting',
                target_id=posting.pk,
            )
        return Response(JobPostingSerializer(posting).data)


class CandidateListCreateView(APIView):
    """`GET, POST, PATCH /api/candidates/`, `docs/06-api-contracts.md` §4.6.
    `POST` is multipart with an optional `resume` file — same object-storage
    pattern as `employee_document` (ADR-0007), `resume_object_key` is
    generated server-side, never taken from the client filename."""

    permission_classes = [CanWriteRecruitment]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        queryset = Candidate.objects.order_by('-created_at')
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(email__icontains=search)
        return Response(CandidateSerializer(queryset, many=True).data)

    def post(self, request):
        serializer = CandidateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        resume_file = request.data.get('resume')
        object_key = None
        if resume_file:
            if resume_file.size > MAX_RESUME_SIZE_BYTES:
                return Response({'detail': 'resume exceeds the maximum allowed size.'}, status=status.HTTP_400_BAD_REQUEST)
            content_type = storage.sniff_content_type(resume_file)
            if content_type is None:
                return Response({'detail': 'unrecognised file type.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                candidate = serializer.save()
                if resume_file:
                    requested_key = storage.generate_resume_object_key(candidate.pk, content_type)
                    object_key = storage.save_document(requested_key, resume_file)
                    candidate.resume_object_key = object_key
                    candidate.save(update_fields=['resume_object_key'])
                audit.services.record(
                    category=AuditLog.CATEGORY_RECORD_CHANGE,
                    action='candidate_created',
                    actor=request.user,
                    target_type='candidate',
                    target_id=candidate.pk,
                )
        except Exception:
            # The resume, if any, was already written to storage before this
            # block; a failed metadata write must not leave it orphaned there
            # with no `candidate` row pointing to it.
            if object_key:
                storage.delete_document(object_key)
            raise
        return Response(CandidateSerializer(candidate).data, status=status.HTTP_201_CREATED)


class CandidateDetailView(APIView):
    """`PATCH /api/candidates/{id}/`, `docs/06-api-contracts.md` §4.6."""

    permission_classes = [CanWriteRecruitment]

    def get(self, request, pk):
        candidate = get_object_or_404(Candidate, pk=pk)
        return Response(CandidateSerializer(candidate).data)

    def patch(self, request, pk):
        candidate = get_object_or_404(Candidate, pk=pk)
        serializer = CandidateSerializer(candidate, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            candidate = serializer.save()
            audit.services.record(
                category=AuditLog.CATEGORY_RECORD_CHANGE,
                action='candidate_updated',
                actor=request.user,
                target_type='candidate',
                target_id=candidate.pk,
            )
        return Response(CandidateSerializer(candidate).data)


class CandidateApplicationListCreateView(APIView):
    """`GET, POST /api/candidates/{id}/applications/`,
    `docs/06-api-contracts.md` §4.6. Maps to `candidate_application`."""

    permission_classes = [CanWriteRecruitment]

    def get(self, request, pk):
        candidate = get_object_or_404(Candidate, pk=pk)
        applications = candidate.applications.order_by('-applied_at')
        return Response(CandidateApplicationSerializer(applications, many=True).data)

    def post(self, request, pk):
        candidate = get_object_or_404(Candidate, pk=pk)
        serializer = CandidateApplicationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # `candidate` is not a serializer field (it's set here from the URL,
        # not the request body), so DRF's automatic UniqueTogetherValidator
        # never sees it — the `(candidate, posting)` uniqueness the model's
        # `UniqueConstraint` enforces has to be checked explicitly here too.
        if CandidateApplication.objects.filter(candidate=candidate, posting=serializer.validated_data['posting']).exists():
            return Response(
                {'detail': 'this candidate has already applied to this posting.'}, status=status.HTTP_400_BAD_REQUEST,
            )
        with transaction.atomic():
            application = serializer.save(candidate=candidate)
            audit.services.record(
                category=AuditLog.CATEGORY_RECORD_CHANGE,
                action='candidate_application_created',
                actor=request.user,
                target_type='candidate_application',
                target_id=application.pk,
            )
        return Response(CandidateApplicationSerializer(application).data, status=status.HTTP_201_CREATED)


class InterviewListCreateView(APIView):
    """`GET, POST, PATCH /api/applications/{id}/interviews/`,
    `docs/06-api-contracts.md` §4.6. `interviewer_employee_id` may reference
    any employee, not only HR Administrators — HRMS-FR-018 does not restrict who
    may interview, only who may schedule."""

    permission_classes = [CanWriteRecruitment]

    def get(self, request, pk):
        application = get_object_or_404(CandidateApplication, pk=pk)
        interviews = application.interviews.order_by('-scheduled_at')
        return Response(InterviewSerializer(interviews, many=True).data)

    def post(self, request, pk):
        application = get_object_or_404(CandidateApplication, pk=pk)
        serializer = InterviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            interview = serializer.save(application=application)
            audit.services.record(
                category=AuditLog.CATEGORY_RECORD_CHANGE,
                action='interview_scheduled',
                actor=request.user,
                target_type='interview',
                target_id=interview.pk,
            )
        return Response(InterviewSerializer(interview).data, status=status.HTTP_201_CREATED)


class InterviewDetailView(APIView):
    """`PATCH /api/applications/{id}/interviews/{interview_id}/`, split from
    the collection endpoint the same way `employees`' emergency-contacts
    endpoints are."""

    permission_classes = [CanWriteRecruitment]

    def patch(self, request, pk, interview_id):
        application = get_object_or_404(CandidateApplication, pk=pk)
        interview = get_object_or_404(Interview, pk=interview_id, application=application)
        serializer = InterviewSerializer(interview, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            interview = serializer.save()
            audit.services.record(
                category=AuditLog.CATEGORY_RECORD_CHANGE,
                action='interview_updated',
                actor=request.user,
                target_type='interview',
                target_id=interview.pk,
            )
        return Response(InterviewSerializer(interview).data)


class OfferLetterListCreateView(APIView):
    """`GET, POST /api/applications/{id}/offer/`, `docs/06-api-contracts.md`
    §4.6. Creates `offer_letter`. `document_object_key` is generated
    server-side once the offer is issued, same object-storage pattern as
    employee documents."""

    permission_classes = [CanWriteRecruitment]

    def get(self, request, pk):
        application = get_object_or_404(CandidateApplication, pk=pk)
        offers = application.offers.order_by('-issued_at')
        return Response(OfferLetterSerializer(offers, many=True).data)

    def post(self, request, pk):
        application = get_object_or_404(CandidateApplication, pk=pk)
        serializer = OfferLetterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        object_key = None
        try:
            with transaction.atomic():
                offer = serializer.save(application=application)
                # Issuing an offer is the recruiter's own act of moving the
                # candidate to the offer stage — nothing else in this app
                # ever advances `stage` (found via the E2E suite: onboarding's
                # convert endpoint requires stage='offer' but no endpoint
                # anywhere set it, making conversion permanently unreachable).
                if application.stage != CandidateApplication.STAGE_OFFER:
                    application.stage = CandidateApplication.STAGE_OFFER
                    application.save(update_fields=['stage', 'updated_at'])
                document_content = (
                    f'Offer Letter\nApplication: {application.pk}\nOffered salary: {offer.offered_salary}\n'
                    f'Issued at: {offer.issued_at.isoformat()}\n'
                )
                object_key = storage.generate_offer_letter_object_key(offer.pk)
                object_key = storage.save_document(object_key, ContentFile(document_content.encode()))
                offer.document_object_key = object_key
                offer.save(update_fields=['document_object_key'])
                audit.services.record(
                    category=AuditLog.CATEGORY_RECORD_CHANGE,
                    action='offer_letter_issued',
                    actor=request.user,
                    target_type='offer_letter',
                    target_id=offer.pk,
                )
        except Exception:
            # The document was already written to storage before this block;
            # a failed metadata write must not leave it orphaned there with
            # no `offer_letter` row pointing to it.
            if object_key:
                storage.delete_document(object_key)
            raise
        return Response(OfferLetterSerializer(offer).data, status=status.HTTP_201_CREATED)


class OfferLetterDecideView(APIView):
    """`POST /api/offers/{id}/decide/`, `docs/06-api-contracts.md` §4.6.
    Records the candidate's decision on their behalf, since a candidate has
    no account (`CONTEXT.md`: "a candidate is not an employee"). An
    `accepted` decision does not itself create an employee record —
    HRMS-BR-013 requires onboarding initiation as the conversion trigger,
    Module 10's endpoint, not this one."""

    permission_classes = [CanWriteRecruitment]

    def post(self, request, pk):
        serializer = OfferDecisionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            offer = get_object_or_404(OfferLetter.objects.select_for_update(), pk=pk)
            if offer.status != OfferLetter.STATUS_PENDING:
                return Response(
                    {'detail': f'offer already decided (status {offer.status!r}).'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            offer.status = serializer.validated_data['decision']
            offer.decided_at = timezone.now()
            offer.save(update_fields=['status', 'decided_at'])
            audit.services.record(
                category=AuditLog.CATEGORY_RECORD_CHANGE,
                action='offer_letter_decided',
                actor=request.user,
                target_type='offer_letter',
                target_id=offer.pk,
            )
        return Response(OfferLetterSerializer(offer).data)
