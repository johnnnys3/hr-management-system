from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from employees.models import Employee

NON_NEGATIVE = MinValueValidator(Decimal('0'))


class SalaryStructure(models.Model):
    """`salary_structure`, `docs/05-database-schema.md` §4.11. HRMS-FR-056.
    The grade framework; `pay_grade` rows belong to one."""

    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True, blank=True)
    effective_from = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'salary_structure'

    def __str__(self):
        return self.name


class PayGrade(models.Model):
    """`pay_grade`, `docs/05-database-schema.md` §4.11. HRMS-FR-057."""

    salary_structure = models.ForeignKey(SalaryStructure, on_delete=models.RESTRICT, related_name='pay_grades')
    name = models.CharField(max_length=255)
    min_salary = models.DecimalField(max_digits=14, decimal_places=2, validators=[NON_NEGATIVE])
    max_salary = models.DecimalField(max_digits=14, decimal_places=2, validators=[NON_NEGATIVE])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'pay_grade'
        constraints = [
            models.CheckConstraint(condition=models.Q(min_salary__gte=0), name='pay_grade_min_salary_gte_0'),
            models.CheckConstraint(condition=models.Q(max_salary__gte=models.F('min_salary')), name='pay_grade_max_gte_min'),
            models.UniqueConstraint(fields=['salary_structure', 'name'], name='pay_grade_unique_name_per_structure'),
        ]

    def __str__(self):
        return f'{self.salary_structure_id} / {self.name}'


class CompensationRecord(models.Model):
    """`compensation_record`, `docs/05-database-schema.md` §4.11.
    HRMS-FR-005, HRMS-FR-058, HRMS-DR-010. Append-only per §3.4: a
    correction is a new row with a later `effective_from`; the prior
    current row is marked superseded (`is_superseded`, `effective_to`)
    rather than rewritten, same shape as `leave_balance`/
    `employment_history`."""

    employee = models.ForeignKey(Employee, on_delete=models.RESTRICT, related_name='compensation_records')
    pay_grade = models.ForeignKey(PayGrade, on_delete=models.RESTRICT, related_name='compensation_records', null=True, blank=True)
    base_salary = models.DecimalField(max_digits=14, decimal_places=2, validators=[NON_NEGATIVE])
    currency = models.CharField(max_length=8, default='GHS')
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)
    is_superseded = models.BooleanField(default=False)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='+',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'compensation_record'
        constraints = [
            models.CheckConstraint(condition=models.Q(base_salary__gte=0), name='compensation_record_base_salary_gte_0'),
            models.UniqueConstraint(
                fields=['employee'], condition=models.Q(is_superseded=False),
                name='compensation_record_one_current_per_employee',
            ),
        ]

    def __str__(self):
        return f'{self.employee_id} @ {self.effective_from} ({self.base_salary})'


class BonusCycle(models.Model):
    """`bonus_cycle`, `docs/05-database-schema.md` §4.11. HRMS-FR-059."""

    STATUS_OPEN = 'open'
    STATUS_CLOSED = 'closed'
    STATUS_CHOICES = [
        (STATUS_OPEN, 'Open'),
        (STATUS_CLOSED, 'Closed'),
    ]

    name = models.CharField(max_length=255)
    period_start = models.DateField()
    period_end = models.DateField()
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_OPEN)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'bonus_cycle'

    def __str__(self):
        return self.name


class BonusAward(models.Model):
    """`bonus_award`, `docs/05-database-schema.md` §4.11. HRMS-FR-059."""

    bonus_cycle = models.ForeignKey(BonusCycle, on_delete=models.RESTRICT, related_name='awards')
    employee = models.ForeignKey(Employee, on_delete=models.RESTRICT, related_name='bonus_awards')
    amount = models.DecimalField(max_digits=14, decimal_places=2, validators=[NON_NEGATIVE])
    awarded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'bonus_award'
        constraints = [
            models.CheckConstraint(condition=models.Q(amount__gte=0), name='bonus_award_amount_gte_0'),
        ]

    def __str__(self):
        return f'{self.bonus_cycle_id} / {self.employee_id} ({self.amount})'


class AllowanceType(models.Model):
    """`allowance_type`, `docs/05-database-schema.md` §4.11. HRMS-FR-060.
    `amount_or_rate` is a fraction (0-1), not a 0-100 percentage, for
    `percentage_of_salary` rows; `fixed` rows keep only the non-negative
    check."""

    CALCULATION_FIXED = 'fixed'
    CALCULATION_PERCENTAGE = 'percentage_of_salary'
    CALCULATION_CHOICES = [
        (CALCULATION_FIXED, 'Fixed'),
        (CALCULATION_PERCENTAGE, 'Percentage of salary'),
    ]

    name = models.CharField(max_length=255, unique=True)
    calculation_method = models.CharField(max_length=32, choices=CALCULATION_CHOICES)
    amount_or_rate = models.DecimalField(max_digits=14, decimal_places=4, validators=[NON_NEGATIVE])
    is_taxable = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'allowance_type'
        constraints = [
            models.CheckConstraint(condition=models.Q(amount_or_rate__gte=0), name='allowance_type_amount_gte_0'),
            models.CheckConstraint(
                condition=~models.Q(calculation_method='percentage_of_salary') | models.Q(amount_or_rate__lte=1),
                name='allowance_type_percentage_rate_lte_1',
            ),
        ]

    def __str__(self):
        return self.name


class EmployeeAllowance(models.Model):
    """`employee_allowance`, `docs/05-database-schema.md` §4.11.
    HRMS-FR-060 per-employee assignment, distinct from the computed
    payslip line amount (module 16)."""

    employee = models.ForeignKey(Employee, on_delete=models.RESTRICT, related_name='allowances')
    allowance_type = models.ForeignKey(AllowanceType, on_delete=models.RESTRICT, related_name='employee_allowances')
    amount_override = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True, validators=[NON_NEGATIVE])
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'employee_allowance'
        constraints = [
            models.CheckConstraint(
                condition=models.Q(amount_override__isnull=True) | models.Q(amount_override__gte=0),
                name='employee_allowance_amount_override_gte_0',
            ),
        ]

    def __str__(self):
        return f'{self.employee_id} / {self.allowance_type_id}'


class Benefit(models.Model):
    """`benefit`, `docs/05-database-schema.md` §4.11. HRMS-FR-061."""

    name = models.CharField(max_length=255, unique=True)
    provider = models.CharField(max_length=255, null=True, blank=True)
    cost = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True, validators=[NON_NEGATIVE])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'benefit'
        constraints = [
            models.CheckConstraint(
                condition=models.Q(cost__isnull=True) | models.Q(cost__gte=0), name='benefit_cost_gte_0'
            ),
        ]

    def __str__(self):
        return self.name


class BenefitEnrollment(models.Model):
    """`benefit_enrollment`, `docs/05-database-schema.md` §4.11.
    HRMS-FR-061. `PATCH {"status": "cancelled"}` sets `cancelled_at`
    (api-contracts §4.13)."""

    STATUS_ACTIVE = 'active'
    STATUS_CANCELLED = 'cancelled'
    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Active'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.RESTRICT, related_name='benefit_enrollments')
    benefit = models.ForeignKey(Benefit, on_delete=models.RESTRICT, related_name='enrollments')
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'benefit_enrollment'

    def __str__(self):
        return f'{self.employee_id} / {self.benefit_id} ({self.status})'
