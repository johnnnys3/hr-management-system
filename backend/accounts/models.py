from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models

CASE_INSENSITIVE_COLLATION = 'case_insensitive'


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('User must have an email address.')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """`user_account`, `docs/05-database-schema.md` §4.2. Custom user model per ADR-0002.

    `employee_id` is not modelled here. Its FK target, `employee`, does not
    exist yet — Employee Management is module 6, not yet built. Module 6
    adds the column and the FK when that table exists, rather than this
    module forward-declaring a table it does not own.
    """

    email = models.EmailField(unique=True, db_collation=CASE_INSENSITIVE_COLLATION)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        db_table = 'user_account'

    def __str__(self):
        return self.email

    def requires_second_factor(self):
        """HRMS-NFR-024: mandatory for administrators and payroll users."""
        return self.groups.filter(name__in=SECOND_FACTOR_REQUIRED_GROUPS).exists()


SECOND_FACTOR_REQUIRED_GROUPS = ['System Administrator', 'Payroll Officer']


class SecondFactor(models.Model):
    """`second_factor`, `docs/05-database-schema.md` §4.2. TOTP per ADR-0012.

    `secret_ref` holds the TOTP shared secret. It is never logged and never
    returned by any endpoint after enrolment.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.RESTRICT,
        related_name='second_factor',
    )
    secret_ref = models.TextField()
    enrolled_at = models.DateTimeField(auto_now_add=True)
    disabled_at = models.DateTimeField(null=True, blank=True)
    last_verified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'second_factor'

    def __str__(self):
        return f'second_factor for user {self.user_id}'


class SecondFactorRecoveryRequest(models.Model):
    """`second_factor_recovery_request`, `docs/05-database-schema.md` §4.2.

    HRMS-NFR-024: recovery requires approval by a user who does not
    administer accounts or credentials. That eligibility check is
    application code (`docs/07-iam-rbac.md` §7.3), not a column here.
    """

    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_DENIED = 'denied'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_DENIED, 'Denied'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.RESTRICT,
        related_name='second_factor_recovery_requests',
    )
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_PENDING)
    requested_at = models.DateTimeField(auto_now_add=True)
    decided_at = models.DateTimeField(null=True, blank=True)
    approver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.RESTRICT,
        null=True,
        blank=True,
        related_name='+',
    )

    class Meta:
        db_table = 'second_factor_recovery_request'
        permissions = [
            ('decide_recovery_request', 'Can approve or deny a second-factor recovery request'),
        ]

    def __str__(self):
        return f'recovery request for user {self.user_id} ({self.status})'
