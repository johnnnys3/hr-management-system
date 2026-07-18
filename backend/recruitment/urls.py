from django.urls import path

from .views import (
    CandidateApplicationListCreateView,
    CandidateDetailView,
    CandidateListCreateView,
    InterviewDetailView,
    InterviewListCreateView,
    JobPostingDetailView,
    JobPostingListCreateView,
    JobPostingPublishView,
    JobRequisitionApproveView,
    JobRequisitionDetailView,
    JobRequisitionListCreateView,
    JobRequisitionRejectView,
    OfferLetterDecideView,
    OfferLetterListCreateView,
)

urlpatterns = [
    path('job-requisitions/', JobRequisitionListCreateView.as_view(), name='job-requisitions'),
    path('job-requisitions/<int:pk>/', JobRequisitionDetailView.as_view(), name='job-requisition-detail'),
    path('job-requisitions/<int:pk>/approve/', JobRequisitionApproveView.as_view(), name='job-requisition-approve'),
    path('job-requisitions/<int:pk>/reject/', JobRequisitionRejectView.as_view(), name='job-requisition-reject'),
    path('job-postings/', JobPostingListCreateView.as_view(), name='job-postings'),
    path('job-postings/<int:pk>/', JobPostingDetailView.as_view(), name='job-posting-detail'),
    path('job-postings/<int:pk>/publish/', JobPostingPublishView.as_view(), name='job-posting-publish'),
    path('candidates/', CandidateListCreateView.as_view(), name='candidates'),
    path('candidates/<int:pk>/', CandidateDetailView.as_view(), name='candidate-detail'),
    path(
        'candidates/<int:pk>/applications/',
        CandidateApplicationListCreateView.as_view(),
        name='candidate-applications',
    ),
    path('applications/<int:pk>/interviews/', InterviewListCreateView.as_view(), name='application-interviews'),
    path(
        'applications/<int:pk>/interviews/<int:interview_id>/',
        InterviewDetailView.as_view(),
        name='application-interview-detail',
    ),
    path('applications/<int:pk>/offer/', OfferLetterListCreateView.as_view(), name='application-offer'),
    path('offers/<int:pk>/decide/', OfferLetterDecideView.as_view(), name='offer-decide'),
]
