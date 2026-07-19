from django.urls import path

from .views import (
    AllowanceTypeDetailView,
    AllowanceTypeListCreateView,
    BenefitDetailView,
    BenefitEnrollmentDetailView,
    BenefitEnrollmentListCreateView,
    BenefitListCreateView,
    BonusAwardListCreateView,
    BonusCycleDetailView,
    BonusCycleListCreateView,
    CompensationRecordListCreateView,
    EmployeeAllowanceListCreateView,
    PayGradeDetailView,
    PayGradeListCreateView,
    SalaryStructureDetailView,
    SalaryStructureListCreateView,
)

urlpatterns = [
    path('salary-structures/', SalaryStructureListCreateView.as_view(), name='salary-structures'),
    path('salary-structures/<int:pk>/', SalaryStructureDetailView.as_view(), name='salary-structure-detail'),
    path('pay-grades/', PayGradeListCreateView.as_view(), name='pay-grades'),
    path('pay-grades/<int:pk>/', PayGradeDetailView.as_view(), name='pay-grade-detail'),
    path(
        'employees/<int:pk>/compensation-records/',
        CompensationRecordListCreateView.as_view(),
        name='employee-compensation-records',
    ),
    path('bonus-cycles/', BonusCycleListCreateView.as_view(), name='bonus-cycles'),
    path('bonus-cycles/<int:pk>/', BonusCycleDetailView.as_view(), name='bonus-cycle-detail'),
    path('bonus-cycles/<int:pk>/awards/', BonusAwardListCreateView.as_view(), name='bonus-cycle-awards'),
    path('allowance-types/', AllowanceTypeListCreateView.as_view(), name='allowance-types'),
    path('allowance-types/<int:pk>/', AllowanceTypeDetailView.as_view(), name='allowance-type-detail'),
    path(
        'employees/<int:pk>/allowances/',
        EmployeeAllowanceListCreateView.as_view(),
        name='employee-allowances',
    ),
    path('benefits/', BenefitListCreateView.as_view(), name='benefits'),
    path('benefits/<int:pk>/', BenefitDetailView.as_view(), name='benefit-detail'),
    path(
        'employees/<int:pk>/benefit-enrollments/',
        BenefitEnrollmentListCreateView.as_view(),
        name='employee-benefit-enrollments',
    ),
    path(
        'employees/<int:pk>/benefit-enrollments/<int:enrollment_id>/',
        BenefitEnrollmentDetailView.as_view(),
        name='employee-benefit-enrollment-detail',
    ),
]
