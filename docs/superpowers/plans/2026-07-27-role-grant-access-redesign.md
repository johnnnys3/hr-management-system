# Role Grant / Access Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Redesign the Role Grant Requests feature into a friendlier "Access" page, per `docs/superpowers/specs/2026-07-27-role-grant-access-redesign.md`: restrict raising a request to System Administrator, default-assign the approval permission to HR Administrator, and replace raw-ID forms/tables with named pickers and plain-language copy — without touching the underlying self-grant/distinct-approver database constraints.

**Architecture:** Two small, real backend changes (a narrowed permission class, a new default-permission migration) plus additive serializer fields for display; one frontend page (`/access`) with two independently role-gated sections consuming the same existing API functions, replacing the current `/role-grant-requests` page.

**Tech Stack:** Django REST Framework, Django migrations, React 19 + Ant Design, TanStack Query, Vitest/Testing Library, Django's own `manage.py test`.

---

## File Structure

- **Modify:** `backend/iam/views.py` — `RoleGrantRequestCreateView.post` permission narrows to System Administrator.
- **Modify:** `backend/iam/tests/test_role_grant_requests.py` — existing tests updated for the narrowed permission; one existing test flips (HR Administrator now IS granted the approval permission by default).
- **Create:** `backend/iam/migrations/0003_grant_approve_role_grant_to_hr_administrator.py`.
- **Modify:** `backend/iam/serializers.py` — `RoleGrantRequestSerializer` gains readable fields; `UserAdminSerializer` gains `employee_name`.
- **Modify:** `backend/iam/tests/test_role_grant_requests.py` (same file as above, additional tests for the new serializer fields).
- **Modify:** `backend/iam/tests/test_users.py` — test for `employee_name` on `/api/users/`.
- **Modify:** `docs/07-iam-rbac.md` — §7.3 and §8 amended.
- **Modify:** `docs/06-api-contracts.md` — §4.9 POST row amended.
- **Modify:** `frontend/src/api/types.ts` — `RoleGrantRequestRecordSchema` and `UserAccountSchema` gain the new fields.
- **Modify:** `frontend/src/layout/navGroups.ts` — "Role Grant Requests" item replaced by role-gated "Grant Access"/"Access Approvals" (single route, label varies).
- **Modify:** `frontend/src/layout/navGroups.test.ts` — updated for the new gating.
- **Modify:** `frontend/src/layout/AppLayout.test.tsx` — if it asserts on "Role Grant Requests" text, update to match.
- **Create:** `frontend/src/modules/rbac/GrantAccessForm.tsx` — the System Administrator's create-request form.
- **Create:** `frontend/src/modules/rbac/GrantAccessForm.test.tsx`.
- **Create:** `frontend/src/modules/rbac/AccessApprovalsQueue.tsx` — the HR Administrator's pending-queue/history view.
- **Create:** `frontend/src/modules/rbac/AccessApprovalsQueue.test.tsx`.
- **Create:** `frontend/src/modules/rbac/AccessPage.tsx` — assembles both sections, gated on `me.groups`.
- **Create:** `frontend/src/modules/rbac/AccessPage.test.tsx`.
- **Delete:** `frontend/src/modules/rbac/RoleGrantRequestsPage.tsx`, `frontend/src/modules/rbac/RoleGrantRequestsPage.test.tsx`.
- **Modify:** `frontend/src/routes.tsx` — `/role-grant-requests` route replaced by `/access`.

---

## Task 1: Restrict raising a request to System Administrator

**Files:**
- Modify: `backend/iam/views.py`
- Modify: `backend/iam/tests/test_role_grant_requests.py`

- [ ] **Step 1: Update the failing tests first**

Open `backend/iam/tests/test_role_grant_requests.py`. The `CreateRoleGrantRequestTests` class currently uses a plain `self.requester` (no group) and expects `201`/`400` responses that will become `403` once the permission narrows. Replace the whole `CreateRoleGrantRequestTests` class with:

```python
class CreateRoleGrantRequestTests(APITestCase):
    def setUp(self):
        self.requester = User.objects.create_user(email='admin@example.com', password='x')
        self.requester.groups.add(Group.objects.get(name=SYSTEM_ADMINISTRATOR))
        self.subject = User.objects.create_user(email='subject@example.com', password='x')
        self.payroll_officer = Group.objects.get(name=PAYROLL_OFFICER)
        self.recruiter = Group.objects.get(name=RECRUITER)

    def test_an_unrelated_group_cannot_be_requested(self):
        """`role_id` is restricted to the six assigned-role groups
        (`docs/07-iam-rbac.md` §2.3) — an arbitrary Django group unrelated
        to RBAC must not be requestable, let alone auto-granted."""
        unrelated_group = Group.objects.create(name='Some Other App Group')
        self.client.force_authenticate(self.requester)

        response = self.client.post(REQUESTS_URL, {
            'subject_user_id': self.subject.pk, 'role_id': unrelated_group.pk,
        })

        self.assertEqual(response.status_code, 400)
        self.assertFalse(self.subject.groups.filter(name='Some Other App Group').exists())

    def test_system_administrator_can_request_a_grant_for_another_user(self):
        self.client.force_authenticate(self.requester)

        response = self.client.post(REQUESTS_URL, {
            'subject_user_id': self.subject.pk, 'role_id': self.payroll_officer.pk,
        })

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['status'], 'pending')

    def test_non_system_administrator_cannot_request_a_grant(self):
        non_admin = User.objects.create_user(email='not-admin@example.com', password='x')
        self.client.force_authenticate(non_admin)

        response = self.client.post(REQUESTS_URL, {
            'subject_user_id': self.subject.pk, 'role_id': self.payroll_officer.pk,
        })

        self.assertEqual(response.status_code, 403)
        self.assertFalse(RoleGrantRequest.objects.exists())

    def test_self_grant_is_refused_at_the_api_layer(self):
        self.client.force_authenticate(self.requester)

        response = self.client.post(REQUESTS_URL, {
            'subject_user_id': self.requester.pk, 'role_id': self.payroll_officer.pk,
        })

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error']['code'], 'self_grant_forbidden')
        self.assertFalse(RoleGrantRequest.objects.exists())

    def test_self_grant_is_refused_at_the_database_layer(self):
        """Defence in depth: the `CHECK` constraint, not just the view,
        is what `docs/06-api-contracts.md` §4.9 cites as the enforcement."""
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                RoleGrantRequest.objects.create(
                    requester=self.requester, subject=self.requester, role=self.payroll_officer,
                )

    def test_anonymous_cannot_request_a_grant(self):
        response = self.client.post(REQUESTS_URL, {
            'subject_user_id': self.subject.pk, 'role_id': self.payroll_officer.pk,
        })

        self.assertEqual(response.status_code, 401)

    def test_non_privileged_role_grant_takes_effect_immediately(self):
        self.client.force_authenticate(self.requester)

        response = self.client.post(REQUESTS_URL, {
            'subject_user_id': self.subject.pk, 'role_id': self.recruiter.pk,
        })

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['status'], 'approved')
        self.assertTrue(self.subject.groups.filter(name=RECRUITER).exists())

    def test_privileged_role_grant_does_not_take_effect_until_approved(self):
        self.client.force_authenticate(self.requester)

        response = self.client.post(REQUESTS_URL, {
            'subject_user_id': self.subject.pk, 'role_id': self.payroll_officer.pk,
        })

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['status'], 'pending')
        self.assertFalse(self.subject.groups.filter(name=PAYROLL_OFFICER).exists())
```

`ListRoleGrantRequestTests` and `DecideRoleGrantRequestTests` are unaffected by this task (they don't exercise `POST /api/role-grant-requests/`) — leave them as-is for now.

- [ ] **Step 2: Run tests to verify the new ones fail**

Run: `docker compose run --rm --entrypoint "" django-migrate python manage.py test iam.tests.test_role_grant_requests.CreateRoleGrantRequestTests -v 2`
Expected: FAIL — `test_non_system_administrator_cannot_request_a_grant` gets `201` not `403` (permission not narrowed yet); `test_system_administrator_can_request_a_grant_for_another_user` still passes (it already could, since `IsFullyAuthenticated` didn't reject a System Administrator either) — the meaningful new failure is the non-admin test.

- [ ] **Step 3: Narrow the permission**

In `backend/iam/views.py`, change `RoleGrantRequestCreateView`'s `permission_classes` and docstring:

```python
class RoleGrantRequestCreateView(APIView):
    """`POST /api/role-grant-requests/`, `docs/06-api-contracts.md` §4.9.

    Raising a request is restricted to System Administrator
    (`docs/07-iam-rbac.md` §7.3, amended 2026-07-27) — narrowed from "any
    authenticated user" as part of the Access redesign
    (`docs/superpowers/specs/2026-07-27-role-grant-access-redesign.md`).
    `GET` on this same view stays open to any authenticated user, since it
    only ever returns the caller's own requests plus requests awaiting
    their decision — narrowing `POST` doesn't change what `GET` can show.

    The self-grant refusal is enforced by the database `CHECK` constraint;
    this view turns the resulting `IntegrityError`-shaped failure into the
    documented `self_grant_forbidden` response rather than a 500, since a
    self-grant is a routine, expected rejection, not a server fault.
    """

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsSystemAdministrator()]
        return [IsFullyAuthenticated()]
```

Remove the class-level `permission_classes = [IsFullyAuthenticated]` line — `get_permissions` replaces it. `IsSystemAdministrator` is already imported in this file (`from .permissions import CanDecideRoleGrantRequest, IsFullyAuthenticated, IsSystemAdministrator`).

- [ ] **Step 4: Run tests to verify they pass**

Run: `docker compose run --rm --entrypoint "" django-migrate python manage.py test iam.tests.test_role_grant_requests -v 2`
Expected: PASS, all tests in the file (the `Create`, `List`, and `Decide` classes together).

- [ ] **Step 5: Run the full iam suite for regressions**

Run: `docker compose run --rm --entrypoint "" django-migrate python manage.py test iam -v 2`
Expected: PASS, all suites.

- [ ] **Step 6: Commit**

```bash
git add backend/iam/views.py backend/iam/tests/test_role_grant_requests.py
git commit -m "Restrict raising a role-grant request to System Administrator"
```

---

## Task 2: Default-assign the approval permission to HR Administrator

**Files:**
- Create: `backend/iam/migrations/0003_grant_approve_role_grant_to_hr_administrator.py`
- Modify: `backend/iam/tests/test_role_grant_requests.py`

- [ ] **Step 1: Update the now-false test first**

In `backend/iam/tests/test_role_grant_requests.py`, find `test_hr_administrator_is_not_granted_approve_role_grant_by_default` (in `DecideRoleGrantRequestTests`) and replace it:

```python
    def test_hr_administrator_is_granted_approve_role_grant_by_default(self):
        """`docs/07-iam-rbac.md` §7.3/§8 (amended 2026-07-27): the
        deployment-configured approver defaults to HR Administrator, which
        already satisfies HRMS-NFR-024's scope requirement for the role and
        is not System Administrator — the migration in this task closes
        what was previously an open deployment question."""
        hr_admin_group = Group.objects.get(name=HR_ADMINISTRATOR)
        permission = Permission.objects.get(codename='approve_role_grant')

        self.assertIn(permission, hr_admin_group.permissions.all())
```

Leave `test_approve_role_grant_is_not_granted_to_system_administrator_by_default` untouched — that guarantee doesn't change.

- [ ] **Step 2: Run the test to verify it fails**

Run: `docker compose run --rm --entrypoint "" django-migrate python manage.py test iam.tests.test_role_grant_requests.DecideRoleGrantRequestTests.test_hr_administrator_is_granted_approve_role_grant_by_default -v 2`
Expected: FAIL — HR Administrator does not yet hold the permission.

- [ ] **Step 3: Write the migration**

```python
# backend/iam/migrations/0003_grant_approve_role_grant_to_hr_administrator.py
from django.db import migrations

# Hard-coded rather than imported from `iam.roles`/`iam.models`, same
# reasoning as 0002_create_assigned_role_groups.py: a historical migration
# must not depend on application code that can change after this migration
# is written.
HR_ADMINISTRATOR_GROUP_NAME = 'HR Administrator'
APPROVE_ROLE_GRANT_CODENAME = 'approve_role_grant'


def grant_permission(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    hr_administrator = Group.objects.get(name=HR_ADMINISTRATOR_GROUP_NAME)
    permission = Permission.objects.get(codename=APPROVE_ROLE_GRANT_CODENAME)
    hr_administrator.permissions.add(permission)


class Migration(migrations.Migration):

    dependencies = [
        ('iam', '0002_create_assigned_role_groups'),
    ]

    operations = [
        # No-op reverse: revoking this on rollback would retroactively
        # invalidate approvals already made under it, the same reasoning
        # 0002's no-op reverse gives for not deleting groups.
        migrations.RunPython(grant_permission, migrations.RunPython.noop),
    ]
```

- [ ] **Step 4: Apply the migration and run the test to verify it passes**

```bash
docker compose run --rm --entrypoint "" django-migrate python manage.py migrate iam
docker compose run --rm --entrypoint "" django-migrate python manage.py test iam.tests.test_role_grant_requests -v 2
```
Expected: PASS, all tests in the file.

- [ ] **Step 5: Run the full iam suite for regressions**

Run: `docker compose run --rm --entrypoint "" django-migrate python manage.py test iam -v 2`
Expected: PASS, all suites.

- [ ] **Step 6: Commit**

```bash
git add backend/iam/migrations/0003_grant_approve_role_grant_to_hr_administrator.py backend/iam/tests/test_role_grant_requests.py
git commit -m "Default-assign iam.approve_role_grant to HR Administrator"
```

---

## Task 3: Readable serializer fields

**Files:**
- Modify: `backend/iam/serializers.py`
- Modify: `backend/iam/tests/test_role_grant_requests.py`
- Modify: `backend/iam/tests/test_users.py`

- [ ] **Step 1: Write the failing tests**

Append to `backend/iam/tests/test_role_grant_requests.py`, inside `ListRoleGrantRequestTests`:

```python
    def test_list_includes_readable_display_fields(self):
        self.client.force_authenticate(self.requester)

        response = self.client.get(REQUESTS_URL)

        record = response.data[0]
        self.assertEqual(record['requester_email'], self.requester.email)
        self.assertEqual(record['subject_email'], self.subject.email)
        self.assertEqual(record['role_name'], PAYROLL_OFFICER)
        self.assertIsNone(record['subject_name'])

    def test_subject_name_reflects_a_linked_employee(self):
        from employees.models import Employee

        employee = Employee.objects.create(
            employee_number='E100', first_name='Jane', last_name='Doe',
            department=None, job_title='Analyst', employment_status=Employee.STATUS_ACTIVE,
            hire_date='2026-01-01', phone='+15550001111',
        )
        self.subject.employee = employee
        self.subject.save(update_fields=['employee'])
        self.client.force_authenticate(self.requester)

        response = self.client.get(REQUESTS_URL)

        self.assertEqual(response.data[0]['subject_name'], 'Jane Doe')
```

Check `Employee.objects.create(...)`'s required fields against `backend/employees/models.py` before running — if `department` is not nullable, or other required fields differ from what's shown here, adjust the `Employee.objects.create(...)` call to match the actual model (read the file first; don't guess blindly if this errors).

- [ ] **Step 2: Write the failing test for `/api/users/`**

Append to `backend/iam/tests/test_users.py` (read the file first to match its existing `setUp`/fixtures rather than assuming — add a test class or method following its established pattern):

```python
    def test_employee_name_is_included_when_linked(self):
        from employees.models import Employee

        employee = Employee.objects.create(
            employee_number='E200', first_name='Ada', last_name='Lovelace',
            department=None, job_title='Engineer', employment_status=Employee.STATUS_ACTIVE,
            hire_date='2026-01-01', phone='+15550002222',
        )
        target_user = User.objects.create_user(email='ada@example.com', password='x', employee=employee)
        self.client.force_authenticate(self.admin)

        response = self.client.get('/api/users/')

        record = next(u for u in response.data if u['id'] == target_user.pk)
        self.assertEqual(record['employee_name'], 'Ada Lovelace')

    def test_employee_name_is_null_when_unlinked(self):
        target_user = User.objects.create_user(email='unlinked@example.com', password='x')
        self.client.force_authenticate(self.admin)

        response = self.client.get('/api/users/')

        record = next(u for u in response.data if u['id'] == target_user.pk)
        self.assertIsNone(record['employee_name'])
```

Match this to the actual `self.admin`/fixture names already in `test_users.py`'s `setUp` — read the file first.

- [ ] **Step 3: Run tests to verify they fail**

Run: `docker compose run --rm --entrypoint "" django-migrate python manage.py test iam.tests.test_role_grant_requests iam.tests.test_users -v 2`
Expected: FAIL — `requester_email`/`subject_email`/`subject_name`/`role_name`/`employee_name` are `KeyError`s (fields don't exist yet).

- [ ] **Step 4: Implement the serializer changes**

In `backend/iam/serializers.py`, replace `RoleGrantRequestSerializer` with:

```python
class RoleGrantRequestSerializer(serializers.ModelSerializer):
    requester_email = serializers.EmailField(source='requester.email', read_only=True)
    subject_email = serializers.EmailField(source='subject.email', read_only=True)
    subject_name = serializers.SerializerMethodField()
    role_name = serializers.CharField(source='role.name', read_only=True)

    class Meta:
        model = RoleGrantRequest
        fields = [
            'id', 'requester', 'subject', 'role', 'status', 'approver', 'requested_at', 'decided_at',
            'requester_email', 'subject_email', 'subject_name', 'role_name',
        ]
        read_only_fields = fields

    def get_subject_name(self, obj):
        employee = getattr(obj.subject, 'employee', None)
        if employee is None:
            return None
        return f'{employee.first_name} {employee.last_name}'
```

And add `employee_name` to `UserAdminSerializer`:

```python
class UserAdminSerializer(serializers.ModelSerializer):
    """... (existing docstring unchanged) ..."""

    password = serializers.CharField(write_only=True, required=False, trim_whitespace=False)
    groups = serializers.SlugRelatedField(many=True, read_only=True, slug_field='name')
    employee_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'is_active', 'groups', 'password', 'employee_name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_employee_name(self, user):
        employee = getattr(user, 'employee', None)
        if employee is None:
            return None
        return f'{employee.first_name} {employee.last_name}'

    # ... existing create()/update() unchanged ...
```

Only add the `employee_name` field and its method — leave `create`/`update` exactly as they are.

- [ ] **Step 5: Run tests to verify they pass**

Run: `docker compose run --rm --entrypoint "" django-migrate python manage.py test iam.tests.test_role_grant_requests iam.tests.test_users -v 2`
Expected: PASS, all tests.

- [ ] **Step 6: Run the full iam suite for regressions**

Run: `docker compose run --rm --entrypoint "" django-migrate python manage.py test iam -v 2`
Expected: PASS, all suites.

- [ ] **Step 7: Commit**

```bash
git add backend/iam/serializers.py backend/iam/tests/test_role_grant_requests.py backend/iam/tests/test_users.py
git commit -m "Add readable display fields to role-grant and user serializers"
```

---

## Task 4: Documentation — IAM and API contracts

**Files:**
- Modify: `docs/07-iam-rbac.md`
- Modify: `docs/06-api-contracts.md`

- [ ] **Step 1: Amend §7.3**

In `docs/07-iam-rbac.md`, find the table row in §7.3 stating who may raise a privileged-role grant request (search for the phrasing that matches "any authenticated user may raise a request" or the table structure around line 288). Update the requester description to specify System Administrator, referencing the redesign:

Add a sentence after the existing §7.3 explanation (find the paragraph discussing the request-raising side, near where it currently doesn't restrict it): "Raising a request is restricted to System Administrator (amended 2026-07-27, `docs/superpowers/specs/2026-07-27-role-grant-access-redesign.md`) — narrowed from any authenticated user. This does not change the approval-side constraint above: the approver must still not be the requester."

- [ ] **Step 2: Amend §8's `iam.approve_role_grant` holder row**

Find the §8 open-items table row for "`iam.approve_role_grant` holder" (currently states "Deferred to deployment... Requires an operating organisation (TBD-001)"). Change its resolution to:

"**Resolved 2026-07-27.** Defaults to HR Administrator via migration (`backend/iam/migrations/0003_grant_approve_role_grant_to_hr_administrator.py`) — already within HRMS-NFR-024's scope and not System Administrator, so the §7.3 enforcement boundary is unaffected. See `docs/superpowers/specs/2026-07-27-role-grant-access-redesign.md`."

- [ ] **Step 3: Add a revision-history row**

Find the revision history table near the top of `docs/07-iam-rbac.md` (same table cited in `CONTEXT.md`'s glossary entries) and check its current highest version number before choosing the next one (don't assume — read the table, the same mistake almost happened on the SRS in an earlier piece of this project). Add a row describing: requester restricted to System Administrator; `iam.approve_role_grant` holder resolved to HR Administrator by default; neither change affects the self-grant or distinct-approver database constraints.

- [ ] **Step 4: Amend `docs/06-api-contracts.md` §4.9**

Find the `POST /api/role-grant-requests/` row (currently: "Any authenticated user — requesting a grant carries no permission of its own..."). Change the Permission column to: "System Administrator (`docs/07-iam-rbac.md` §7.3, amended 2026-07-27) — narrowed from any authenticated user as part of the Access redesign." Leave the `GET` row on the same endpoint unchanged — its permission didn't change.

- [ ] **Step 5: Commit**

```bash
git add docs/07-iam-rbac.md docs/06-api-contracts.md
git commit -m "Document restricted role-grant requester and default HR Administrator approver"
```

---

## Task 5: Frontend types for the new fields

**Files:**
- Modify: `frontend/src/api/types.ts`

- [ ] **Step 1: Update `RoleGrantRequestRecordSchema`**

In `frontend/src/api/types.ts`, find `RoleGrantRequestRecordSchema` and add the new fields:

```typescript
export const RoleGrantRequestRecordSchema = z.object({
  id: z.number(),
  requester: z.number(),
  subject: z.number(),
  role: z.number(),
  status: z.enum(['pending', 'approved', 'refused']),
  approver: z.number().nullable(),
  requested_at: z.string(),
  decided_at: z.string().nullable(),
  requester_email: z.string(),
  subject_email: z.string(),
  subject_name: z.string().nullable(),
  role_name: z.string(),
})
export type RoleGrantRequestRecord = z.infer<typeof RoleGrantRequestRecordSchema>
```

- [ ] **Step 2: Update `UserAccountSchema`**

Find `UserAccountSchema` and add `employee_name`:

```typescript
export const UserAccountSchema = z.object({
  id: z.number(),
  email: z.string(),
  is_active: z.boolean(),
  groups: z.array(z.string()),
  employee_name: z.string().nullable(),
  created_at: z.string(),
  updated_at: z.string(),
})
export type UserAccount = z.infer<typeof UserAccountSchema>
```

- [ ] **Step 3: Typecheck**

Run: `cd frontend && npx tsc -b`
Expected: errors in `RoleGrantRequestsPage.tsx`/`RoleGrantRequestsPage.test.tsx` and `frontend/src/modules/rbac/*.test.tsx` (missing the new required fields in mocked records) — these are the files Tasks 6-9 replace/fix. Confirm the errors are ONLY in files this plan goes on to touch (`RoleGrantRequestsPage*`), not elsewhere — if something unrelated breaks, stop and report it rather than proceeding.

- [ ] **Step 4: Commit**

```bash
git add frontend/src/api/types.ts
git commit -m "Add readable display fields to frontend role-grant and user account types"
```

---

## Task 6: Navigation — role-gated "Grant Access" / "Access Approvals"

**Files:**
- Modify: `frontend/src/layout/navGroups.ts`
- Modify: `frontend/src/layout/navGroups.test.ts`
- Modify: `frontend/src/layout/AppLayout.test.tsx` (only if it references the old label — check first)

- [ ] **Step 1: Update the failing tests**

In `frontend/src/layout/navGroups.test.ts`, replace the test that currently expects `/role-grant-requests` for a plain employee:

```typescript
  it('shows only My Work for a plain employee (no Access item at all)', () => {
    const groups = buildNavGroups(makeMe())
    expect(groups.map((g) => g.label)).toEqual(['My Work'])
  })
```

Replace the System Administrator test:

```typescript
  it('shows Grant Access (not Access Approvals) for System Administrator, alongside Users and Audit Log', () => {
    const groups = buildNavGroups(makeMe({ groups: ['System Administrator'] }))
    const admin = groups.find((g) => g.label === 'Admin')
    expect(admin?.items.map((i) => i.key)).toEqual(['/access', '/users', '/audit-log'])
    expect(admin?.items.find((i) => i.key === '/access')?.label).toEqual('Grant Access')
  })
```

Add two new tests:

```typescript
  it('shows Access Approvals (not Grant Access) for HR Administrator', () => {
    const groups = buildNavGroups(makeMe({ groups: ['HR Administrator'] }))
    const admin = groups.find((g) => g.label === 'Admin')
    expect(admin?.items.map((i) => i.key)).toEqual(['/access'])
    expect(admin?.items.find((i) => i.key === '/access')?.label).toEqual('Access Approvals')
  })

  it('shows one combined Access item, not two, for a user holding both roles', () => {
    const groups = buildNavGroups(makeMe({ groups: ['System Administrator', 'HR Administrator'] }))
    const admin = groups.find((g) => g.label === 'Admin')
    expect(admin?.items.filter((i) => i.key === '/access')).toHaveLength(1)
    expect(admin?.items.find((i) => i.key === '/access')?.label).toEqual('Access')
  })
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `npm run test -- navGroups` (from `frontend/`)
Expected: FAIL — current code still emits `/role-grant-requests` unconditionally.

- [ ] **Step 3: Implement the gating**

In `frontend/src/layout/navGroups.ts`, replace the `admin` array construction:

```typescript
  const canGrantAccess = me.groups.includes('System Administrator')
  // Proxy for the `iam.approve_role_grant` permission, which the frontend
  // has no general mechanism to query directly — correct given the
  // migration in backend/iam/migrations/0003_... defaults that permission
  // to this group. Revisit if a deployment ever assigns the permission
  // elsewhere (docs/07-iam-rbac.md §8).
  const canApproveAccess = me.groups.includes('HR Administrator')

  let accessLabel: string | null = null
  if (canGrantAccess && canApproveAccess) {
    accessLabel = 'Access'
  } else if (canGrantAccess) {
    accessLabel = 'Grant Access'
  } else if (canApproveAccess) {
    accessLabel = 'Access Approvals'
  }

  const admin: NavItem[] = [
    ...(accessLabel ? [{ key: '/access', label: accessLabel, icon: 'SafetyCertificateOutlined' }] : []),
    ...(me.groups.includes('System Administrator')
      ? [
          { key: '/users', label: 'Users', icon: 'UsergroupAddOutlined' },
          { key: '/audit-log', label: 'Audit Log', icon: 'FileSearchOutlined' },
        ]
      : []),
  ]
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `npm run test -- navGroups`
Expected: PASS, all tests.

- [ ] **Step 5: Check `AppLayout.test.tsx` for the old label**

Run: `grep -n "Role Grant Requests" frontend/src/layout/AppLayout.test.tsx`

If it appears, update the affected assertion(s) to match the new gating (e.g. a plain-employee test asserting `Role Grant Requests` visible should now assert no "Admin" group at all, matching Task 6 Step 1's `navGroups.test.ts` change). If it doesn't appear, skip this step.

- [ ] **Step 6: Run the full frontend suite for regressions**

Run: `npm run test` (from `frontend/`)
Expected: FAIL only in `RoleGrantRequestsPage*`/`rbac/*` files not yet updated (Tasks 7-9) — everything else PASS. If anything else fails, stop and report before continuing.

- [ ] **Step 7: Commit**

```bash
git add frontend/src/layout/navGroups.ts frontend/src/layout/navGroups.test.ts frontend/src/layout/AppLayout.test.tsx
git commit -m "Replace Role Grant Requests nav item with role-gated Grant Access / Access Approvals"
```

---

## Task 7: Assigned-roles listing endpoint

The frontend role picker (Task 8) needs to show all six assigned roles with their database ids (`auth_group.id` — database-assigned, not something application code can hardcode). No endpoint currently lists them. Build it first, so Task 8 can consume a real API from the start.

**Files:**
- Modify: `backend/iam/views.py`
- Modify: `backend/iam/urls.py`
- Modify: `backend/iam/tests/test_roles.py`
- Modify: `frontend/src/api/rbac.ts`

- [ ] **Step 1: Read `backend/iam/tests/test_roles.py` first**

It may already test `iam.roles` (the Python module of role constants) rather than an HTTP endpoint — confirm what's actually in there before adding to it, so the new test class doesn't duplicate an existing import or fixture pattern.

- [ ] **Step 2: Write the failing tests**

Add to `backend/iam/tests/test_roles.py` (merge imports with what's already there rather than duplicating — it likely already imports `APITestCase`, `get_user_model`, and role constants):

```python
class AssignedRolesListViewTests(APITestCase):
    def test_system_administrator_sees_all_six_assigned_roles(self):
        admin = User.objects.create_user(email='admin2@example.com', password='x')
        admin.groups.add(Group.objects.get(name=SYSTEM_ADMINISTRATOR))
        self.client.force_authenticate(admin)

        response = self.client.get('/api/roles/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual({r['name'] for r in response.data}, set(ASSIGNED_ROLES))

    def test_non_system_administrator_is_denied(self):
        non_admin = User.objects.create_user(email='non-admin2@example.com', password='x')
        self.client.force_authenticate(non_admin)

        response = self.client.get('/api/roles/')

        self.assertEqual(response.status_code, 403)

    def test_anonymous_is_denied(self):
        response = self.client.get('/api/roles/')

        self.assertEqual(response.status_code, 401)
```

Ensure `ASSIGNED_ROLES`, `SYSTEM_ADMINISTRATOR` (from `iam.roles`), `Group` (from `django.contrib.auth.models`), and `User = get_user_model()` are available in the file — add any of these imports that aren't already there.

- [ ] **Step 3: Run tests to verify they fail**

Run: `docker compose run --rm --entrypoint "" django-migrate python manage.py test iam.tests.test_roles -v 2`
Expected: FAIL — `/api/roles/` doesn't exist yet (404).

- [ ] **Step 4: Implement the view**

In `backend/iam/views.py`, add to the imports: `from django.contrib.auth.models import Group` and change the existing `from .roles import RECRUITER` line to `from .roles import ASSIGNED_ROLES, RECRUITER`. Then append:

```python
class AssignedRolesListView(APIView):
    """`GET /api/roles/`. Lists the six assigned-role groups with their
    database ids, so a client can build a role picker without hardcoding
    group ids. System-Administrator-only, since only System Administrator
    raises role-grant requests
    (`docs/superpowers/specs/2026-07-27-role-grant-access-redesign.md`).
    """

    permission_classes = [IsSystemAdministrator]

    def get(self, request):
        groups = Group.objects.filter(name__in=ASSIGNED_ROLES).order_by('name')
        return Response([{'id': g.pk, 'name': g.name} for g in groups])
```

- [ ] **Step 5: Wire the URL**

In `backend/iam/urls.py`:

```python
from .views import (
    AssignedRolesListView,
    RoleGrantRequestCreateView,
    RoleGrantRequestDecideView,
    UserDetailView,
    UserListCreateView,
)

urlpatterns = [
    path('users/', UserListCreateView.as_view(), name='iam-users'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='iam-user-detail'),
    path('roles/', AssignedRolesListView.as_view(), name='iam-roles'),
    path('role-grant-requests/', RoleGrantRequestCreateView.as_view(), name='iam-role-grant-requests'),
    path('role-grant-requests/<int:pk>/decide/', RoleGrantRequestDecideView.as_view(),
         name='iam-role-grant-request-decide'),
]
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `docker compose run --rm --entrypoint "" django-migrate python manage.py test iam.tests.test_roles -v 2`
Expected: PASS, 3 new tests (plus whatever was already in that file).

- [ ] **Step 7: Run the full iam suite for regressions**

Run: `docker compose run --rm --entrypoint "" django-migrate python manage.py test iam -v 2`
Expected: PASS, all suites.

- [ ] **Step 8: Add the frontend client function**

In `frontend/src/api/rbac.ts`, add:

```typescript
export function listAssignedRoles(): Promise<{ id: number; name: string }[]> {
  return apiFetch('/api/roles/')
}
```

- [ ] **Step 9: Commit**

```bash
git add backend/iam/views.py backend/iam/urls.py backend/iam/tests/test_roles.py frontend/src/api/rbac.ts
git commit -m "Add assigned-roles listing endpoint"
```

---

## Task 8: `GrantAccessForm` component

**Files:**
- Create: `frontend/src/modules/rbac/GrantAccessForm.tsx`
- Create: `frontend/src/modules/rbac/GrantAccessForm.test.tsx`

- [ ] **Step 1: Write the failing test**

```typescript
// frontend/src/modules/rbac/GrantAccessForm.test.tsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, describe, expect, it, vi } from 'vitest'
import * as rbacApi from '../../api/rbac'
import { GrantAccessForm } from './GrantAccessForm'

function renderForm() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <GrantAccessForm />
    </QueryClientProvider>,
  )
}

describe('GrantAccessForm', () => {
  afterEach(() => vi.restoreAllMocks())

  it('lists users by email when unlinked to an employee', async () => {
    vi.spyOn(rbacApi, 'listUsers').mockResolvedValue([
      { id: 2, email: 'jane@example.com', is_active: true, groups: [], employee_name: null, created_at: '', updated_at: '' },
    ])
    vi.spyOn(rbacApi, 'listAssignedRoles').mockResolvedValue([])
    renderForm()
    const user = userEvent.setup()

    await user.click(screen.getByLabelText(/who gets access/i))

    expect(await screen.findByText('jane@example.com')).toBeInTheDocument()
  })

  it('lists users by name and email when linked to an employee', async () => {
    vi.spyOn(rbacApi, 'listUsers').mockResolvedValue([
      { id: 2, email: 'jane@example.com', is_active: true, groups: [], employee_name: 'Jane Doe', created_at: '', updated_at: '' },
    ])
    vi.spyOn(rbacApi, 'listAssignedRoles').mockResolvedValue([])
    renderForm()
    const user = userEvent.setup()

    await user.click(screen.getByLabelText(/who gets access/i))

    expect(await screen.findByText('Jane Doe (jane@example.com)')).toBeInTheDocument()
  })

  it('shows a plain-language description for each role option', async () => {
    vi.spyOn(rbacApi, 'listUsers').mockResolvedValue([])
    vi.spyOn(rbacApi, 'listAssignedRoles').mockResolvedValue([{ id: 3, name: 'HR Administrator' }])
    renderForm()
    const user = userEvent.setup()

    await user.click(screen.getByLabelText(/what access/i))

    expect(await screen.findByText(/manage employee records, departments/i)).toBeInTheDocument()
  })

  it('submits a request and shows the pending-approval confirmation for a privileged role', async () => {
    vi.spyOn(rbacApi, 'listUsers').mockResolvedValue([
      { id: 2, email: 'jane@example.com', is_active: true, groups: [], employee_name: 'Jane Doe', created_at: '', updated_at: '' },
    ])
    vi.spyOn(rbacApi, 'listAssignedRoles').mockResolvedValue([{ id: 3, name: 'Payroll Officer' }])
    const createSpy = vi.spyOn(rbacApi, 'createRoleGrantRequest').mockResolvedValue({
      id: 10, requester: 1, subject: 2, role: 3, status: 'pending', approver: null,
      requested_at: '', decided_at: null, requester_email: 'admin@example.com',
      subject_email: 'jane@example.com', subject_name: 'Jane Doe', role_name: 'Payroll Officer',
    })
    renderForm()
    const user = userEvent.setup()

    await user.click(screen.getByLabelText(/who gets access/i))
    await user.click(await screen.findByText('Jane Doe (jane@example.com)'))
    await user.click(screen.getByLabelText(/what access/i))
    await user.click(await screen.findByText(/process payroll and compensation/i))
    await user.click(screen.getByRole('button', { name: /submit/i }))

    await waitFor(() => expect(createSpy).toHaveBeenCalledWith(2, 3))
    expect(await screen.findByText(/awaiting approval from an hr administrator/i)).toBeInTheDocument()
  })

  it('shows the immediate-grant confirmation for Recruiter', async () => {
    vi.spyOn(rbacApi, 'listUsers').mockResolvedValue([
      { id: 2, email: 'jane@example.com', is_active: true, groups: [], employee_name: null, created_at: '', updated_at: '' },
    ])
    vi.spyOn(rbacApi, 'listAssignedRoles').mockResolvedValue([{ id: 4, name: 'Recruiter' }])
    vi.spyOn(rbacApi, 'createRoleGrantRequest').mockResolvedValue({
      id: 11, requester: 1, subject: 2, role: 4, status: 'approved', approver: null,
      requested_at: '', decided_at: '', requester_email: 'admin@example.com',
      subject_email: 'jane@example.com', subject_name: null, role_name: 'Recruiter',
    })
    renderForm()
    const user = userEvent.setup()

    await user.click(screen.getByLabelText(/who gets access/i))
    await user.click(await screen.findByText('jane@example.com'))
    await user.click(screen.getByLabelText(/what access/i))
    await user.click(await screen.findByText(/manage job postings and candidates/i))
    await user.click(screen.getByRole('button', { name: /submit/i }))

    expect(await screen.findByText(/recruiter access granted immediately/i)).toBeInTheDocument()
  })
})
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npm run test -- GrantAccessForm` (from `frontend/`)
Expected: FAIL — module doesn't exist.

- [ ] **Step 3: Implement the component**

```typescript
// frontend/src/modules/rbac/GrantAccessForm.tsx
import { useMutation, useQuery } from '@tanstack/react-query'
import { Alert, Button, Form, Select, Typography } from 'antd'
import { useState } from 'react'
import { ApiError } from '../../api/client'
import { createRoleGrantRequest, listAssignedRoles, listUsers } from '../../api/rbac'

const ROLE_DESCRIPTIONS: Record<string, string> = {
  'System Administrator': 'Manage accounts, roles, and system configuration',
  'HR Administrator': 'Manage employee records, departments, and HR configuration',
  'HR Officer': 'Handle day-to-day HR operations and onboarding',
  'Recruiter': 'Manage job postings and candidates',
  'Payroll Officer': 'Process payroll and compensation',
  'Executive': 'View organization-wide reports',
}

export function GrantAccessForm() {
  const { data: users = [] } = useQuery({ queryKey: ['rbac', 'users'], queryFn: listUsers })
  const { data: roles = [] } = useQuery({ queryKey: ['rbac', 'roles'], queryFn: listAssignedRoles })
  const [subjectUserId, setSubjectUserId] = useState<number | null>(null)
  const [roleId, setRoleId] = useState<number | null>(null)
  const [confirmation, setConfirmation] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const mutation = useMutation({
    mutationFn: () => createRoleGrantRequest(subjectUserId as number, roleId as number),
    onSuccess: (result) => {
      setError(null)
      setConfirmation(
        result.status === 'approved'
          ? `${result.role_name} access granted immediately.`
          : 'Request submitted — awaiting approval from an HR Administrator.',
      )
    },
    onError: (e) => setError(e instanceof ApiError ? e.message : 'Something went wrong. Please try again.'),
  })

  return (
    <div>
      <Typography.Title level={5} style={{ marginTop: 0, marginBottom: 14 }}>
        Grant a user access
      </Typography.Title>
      {confirmation && <Alert type="success" message={confirmation} style={{ marginBottom: 16 }} />}
      {error && <Alert type="error" message={error} style={{ marginBottom: 16 }} />}
      <Form layout="vertical" onFinish={() => mutation.mutate()}>
        <Form.Item label="Who gets access" required>
          <Select
            aria-label="Who gets access"
            style={{ minWidth: 320 }}
            value={subjectUserId ?? undefined}
            onChange={(value) => setSubjectUserId(value)}
            options={users.map((u) => ({
              value: u.id,
              label: u.employee_name ? `${u.employee_name} (${u.email})` : u.email,
            }))}
          />
        </Form.Item>
        <Form.Item label="What access" required>
          <Select
            aria-label="What access"
            style={{ minWidth: 320 }}
            value={roleId ?? undefined}
            onChange={(value) => setRoleId(value)}
            options={roles.map((r) => ({
              value: r.id,
              label: `${r.name} — ${ROLE_DESCRIPTIONS[r.name] ?? ''}`,
            }))}
          />
        </Form.Item>
        <Form.Item>
          <Button type="primary" htmlType="submit" loading={mutation.isPending} disabled={!subjectUserId || !roleId}>
            Submit
          </Button>
        </Form.Item>
      </Form>
    </div>
  )
}
```

- [ ] **Step 4: Run the frontend test to verify it passes**

Run: `npm run test -- GrantAccessForm` (from `frontend/`)
Expected: PASS, 5 tests.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/modules/rbac/GrantAccessForm.tsx frontend/src/modules/rbac/GrantAccessForm.test.tsx
git commit -m "Add GrantAccessForm component"
```

---

## Task 9: `AccessApprovalsQueue` component

**Files:**
- Create: `frontend/src/modules/rbac/AccessApprovalsQueue.tsx`
- Create: `frontend/src/modules/rbac/AccessApprovalsQueue.test.tsx`

- [ ] **Step 1: Write the failing test**

```typescript
// frontend/src/modules/rbac/AccessApprovalsQueue.test.tsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, describe, expect, it, vi } from 'vitest'
import * as rbacApi from '../../api/rbac'
import { AccessApprovalsQueue } from './AccessApprovalsQueue'

function renderQueue() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <AccessApprovalsQueue />
    </QueryClientProvider>,
  )
}

const pendingRequest = {
  id: 11, requester: 1, subject: 2, role: 3, status: 'pending' as const, approver: null,
  requested_at: '2026-07-27T00:00:00Z', decided_at: null,
  requester_email: 'admin@example.com', subject_email: 'jane@example.com',
  subject_name: 'Jane Doe', role_name: 'Payroll Officer',
}

describe('AccessApprovalsQueue', () => {
  afterEach(() => vi.restoreAllMocks())

  it('renders a pending request as a plain-language sentence', async () => {
    vi.spyOn(rbacApi, 'listRoleGrantRequests').mockResolvedValue([pendingRequest])
    renderQueue()

    expect(await screen.findByText(/payroll officer access for jane doe \(jane@example\.com\)/i)).toBeInTheDocument()
  })

  it('approves a pending request', async () => {
    vi.spyOn(rbacApi, 'listRoleGrantRequests').mockResolvedValue([pendingRequest])
    const decideSpy = vi.spyOn(rbacApi, 'decideRoleGrantRequest').mockResolvedValue({
      ...pendingRequest, status: 'approved', approver: 5, decided_at: '2026-07-27T01:00:00Z',
    })
    renderQueue()
    const user = userEvent.setup()

    await screen.findByText(/payroll officer/i)
    await user.click(screen.getByRole('button', { name: /^approve$/i }))
    await user.click(await screen.findByRole('button', { name: 'OK' }))

    await waitFor(() => expect(decideSpy).toHaveBeenCalledWith(11, 'approved'))
  })

  it('declines a pending request', async () => {
    vi.spyOn(rbacApi, 'listRoleGrantRequests').mockResolvedValue([pendingRequest])
    const decideSpy = vi.spyOn(rbacApi, 'decideRoleGrantRequest').mockResolvedValue({
      ...pendingRequest, status: 'refused', approver: 5, decided_at: '2026-07-27T01:00:00Z',
    })
    renderQueue()
    const user = userEvent.setup()

    await screen.findByText(/payroll officer/i)
    await user.click(screen.getByRole('button', { name: /decline/i }))
    await user.click(await screen.findByRole('button', { name: 'OK' }))

    await waitFor(() => expect(decideSpy).toHaveBeenCalledWith(11, 'refused'))
  })

  it('shows decided requests as history, without approve/decline actions', async () => {
    vi.spyOn(rbacApi, 'listRoleGrantRequests').mockResolvedValue([
      { ...pendingRequest, status: 'approved', decided_at: '2026-07-27T01:00:00Z' },
    ])
    renderQueue()

    await screen.findByText(/payroll officer/i)
    expect(screen.queryByRole('button', { name: /^approve$/i })).not.toBeInTheDocument()
  })
})
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npm run test -- AccessApprovalsQueue` (from `frontend/`)
Expected: FAIL — module doesn't exist.

- [ ] **Step 3: Implement the component**

```typescript
// frontend/src/modules/rbac/AccessApprovalsQueue.tsx
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Button, List, Popconfirm, Space, Tag, Typography } from 'antd'
import { decideRoleGrantRequest, listRoleGrantRequests } from '../../api/rbac'
import type { RoleGrantRequestRecord } from '../../api/types'

const REQUESTS_QUERY_KEY = ['rbac', 'role-grant-requests']

export function AccessApprovalsQueue() {
  const queryClient = useQueryClient()
  const { data: requests = [] } = useQuery({ queryKey: REQUESTS_QUERY_KEY, queryFn: listRoleGrantRequests })

  const mutation = useMutation({
    mutationFn: ({ id, decision }: { id: number; decision: 'approved' | 'refused' }) =>
      decideRoleGrantRequest(id, decision),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: REQUESTS_QUERY_KEY }),
  })

  const pending = requests.filter((r) => r.status === 'pending')
  const decided = requests.filter((r) => r.status !== 'pending')

  return (
    <div>
      <Typography.Title level={5} style={{ marginTop: 0, marginBottom: 14 }}>
        Pending approvals
      </Typography.Title>
      <List<RoleGrantRequestRecord>
        dataSource={pending}
        locale={{ emptyText: 'No requests waiting on your decision.' }}
        renderItem={(record) => (
          <List.Item
            actions={[
              <Popconfirm key="approve" title="Approve this request?" onConfirm={() => mutation.mutate({ id: record.id, decision: 'approved' })}>
                <Button size="small" loading={mutation.isPending && mutation.variables?.id === record.id}>
                  Approve
                </Button>
              </Popconfirm>,
              <Popconfirm key="decline" title="Decline this request?" onConfirm={() => mutation.mutate({ id: record.id, decision: 'refused' })}>
                <Button size="small" danger loading={mutation.isPending && mutation.variables?.id === record.id}>
                  Decline
                </Button>
              </Popconfirm>,
            ]}
          >
            {record.requester_email} requests {record.role_name} access for{' '}
            {record.subject_name ? `${record.subject_name} (${record.subject_email})` : record.subject_email}
          </List.Item>
        )}
      />
      <Typography.Title level={5} style={{ marginTop: 32, marginBottom: 14 }}>
        History
      </Typography.Title>
      <List<RoleGrantRequestRecord>
        dataSource={decided}
        locale={{ emptyText: 'No decided requests yet.' }}
        renderItem={(record) => (
          <List.Item>
            <Space>
              <Tag color={record.status === 'approved' ? 'green' : 'red'}>{record.status}</Tag>
              {record.requester_email} requested {record.role_name} access for{' '}
              {record.subject_name ? `${record.subject_name} (${record.subject_email})` : record.subject_email}
            </Space>
          </List.Item>
        )}
      />
    </div>
  )
}
```

- [ ] **Step 4: Run the frontend test to verify it passes**

Run: `npm run test -- AccessApprovalsQueue`
Expected: PASS, 4 tests.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/modules/rbac/AccessApprovalsQueue.tsx frontend/src/modules/rbac/AccessApprovalsQueue.test.tsx
git commit -m "Add AccessApprovalsQueue component"
```

---

## Task 10: Assemble `AccessPage`, wire routing, remove the old page

**Files:**
- Create: `frontend/src/modules/rbac/AccessPage.tsx`
- Create: `frontend/src/modules/rbac/AccessPage.test.tsx`
- Delete: `frontend/src/modules/rbac/RoleGrantRequestsPage.tsx`
- Delete: `frontend/src/modules/rbac/RoleGrantRequestsPage.test.tsx`
- Modify: `frontend/src/routes.tsx`

- [ ] **Step 1: Write the failing test**

```typescript
// frontend/src/modules/rbac/AccessPage.test.tsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import * as rbacApi from '../../api/rbac'
import { AuthContext } from '../../auth/AuthContext'
import { AccessPage } from './AccessPage'
import type { Me } from '../../api/types'

function makeMe(overrides: Partial<Me> = {}): Me {
  return {
    id: 1, email: 'a@b.com', groups: [], is_employee: true, is_manager: false,
    second_factor_enrollment_pending: false, ...overrides,
  }
}

function renderPage(me: Me) {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  vi.spyOn(rbacApi, 'listUsers').mockResolvedValue([])
  vi.spyOn(rbacApi, 'listAssignedRoles').mockResolvedValue([])
  vi.spyOn(rbacApi, 'listRoleGrantRequests').mockResolvedValue([])
  return render(
    <QueryClientProvider client={queryClient}>
      <AuthContext.Provider value={{ me, isLoading: false, refetch: async () => {}, logout: async () => {} }}>
        <AccessPage />
      </AuthContext.Provider>
    </QueryClientProvider>,
  )
}

describe('AccessPage', () => {
  it('shows only Grant Access for a System Administrator who is not also HR Administrator', async () => {
    renderPage(makeMe({ groups: ['System Administrator'] }))
    expect(await screen.findByText('Grant a user access')).toBeInTheDocument()
    expect(screen.queryByText('Pending approvals')).not.toBeInTheDocument()
  })

  it('shows only Access Approvals for an HR Administrator who is not also System Administrator', async () => {
    renderPage(makeMe({ groups: ['HR Administrator'] }))
    expect(await screen.findByText('Pending approvals')).toBeInTheDocument()
    expect(screen.queryByText('Grant a user access')).not.toBeInTheDocument()
  })

  it('shows both sections for a user holding both roles', async () => {
    renderPage(makeMe({ groups: ['System Administrator', 'HR Administrator'] }))
    expect(await screen.findByText('Grant a user access')).toBeInTheDocument()
    expect(await screen.findByText('Pending approvals')).toBeInTheDocument()
  })
})
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npm run test -- AccessPage` (from `frontend/`)
Expected: FAIL — module doesn't exist.

- [ ] **Step 3: Implement the page**

```typescript
// frontend/src/modules/rbac/AccessPage.tsx
import { Typography } from 'antd'
import { useAuth } from '../../auth/AuthContext'
import { AccessApprovalsQueue } from './AccessApprovalsQueue'
import { GrantAccessForm } from './GrantAccessForm'

export function AccessPage() {
  const { me } = useAuth()
  const canGrantAccess = me?.groups.includes('System Administrator') ?? false
  const canApproveAccess = me?.groups.includes('HR Administrator') ?? false

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 32 }}>
      <Typography.Title level={3}>Access</Typography.Title>
      {canGrantAccess && <GrantAccessForm />}
      {canGrantAccess && canApproveAccess && <div style={{ borderTop: '1px solid #ececec' }} />}
      {canApproveAccess && <AccessApprovalsQueue />}
    </div>
  )
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `npm run test -- AccessPage`
Expected: PASS, 3 tests.

- [ ] **Step 5: Remove the old page and wire the new route**

```bash
rm frontend/src/modules/rbac/RoleGrantRequestsPage.tsx frontend/src/modules/rbac/RoleGrantRequestsPage.test.tsx
```

In `frontend/src/routes.tsx`, replace:
```typescript
import { RoleGrantRequestsPage } from './modules/rbac/RoleGrantRequestsPage'
```
with:
```typescript
import { AccessPage } from './modules/rbac/AccessPage'
```
and replace:
```typescript
              { path: '/role-grant-requests', element: <RoleGrantRequestsPage /> },
```
with:
```typescript
              { path: '/access', element: <AccessPage /> },
```

- [ ] **Step 6: Run the full frontend suite for regressions**

Run: `npm run test` (from `frontend/`)
Expected: PASS, all suites.

- [ ] **Step 7: Typecheck**

Run: `cd frontend && npx tsc -b`
Expected: no errors.

- [ ] **Step 8: Commit**

```bash
git add frontend/src/modules/rbac/AccessPage.tsx frontend/src/modules/rbac/AccessPage.test.tsx frontend/src/routes.tsx
git rm frontend/src/modules/rbac/RoleGrantRequestsPage.tsx frontend/src/modules/rbac/RoleGrantRequestsPage.test.tsx
git commit -m "Assemble AccessPage, wire /access route, remove old Role Grant Requests page"
```

---

## Task 11: Full-stack regression run

**Files:** none (verification only)

- [ ] **Step 1: Full backend suite**

Run: `docker compose run --rm --entrypoint "" django-migrate python manage.py test`
Expected: PASS, all apps.

- [ ] **Step 2: Full frontend suite**

Run: `cd frontend && npm run test`
Expected: PASS, all suites.

- [ ] **Step 3: Typecheck**

Run: `cd frontend && npx tsc -b`
Expected: no errors.

- [ ] **Step 4: Manual verification, if a docker stack with seeded fixtures is available**

Log in as the `e2e.sysadmin@example.com` fixture (see `backend/accounts/management/commands/seed_e2e_fixtures.py` for credentials and the TOTP secret needed for its MFA step) and confirm the "Grant Access" nav item and form work end to end against a real backend; log in as an HR Administrator fixture and confirm "Access Approvals" shows the pending request and can decide it. This step is optional if the automated suites above already give confidence — note in your report whether you did it.

- [ ] **Step 5: No commit** — verification only.

---

## Self-Review

**Spec coverage:**
- §3 (backend access control: requester restricted, approver defaulted) → Tasks 1-2.
- §4 (readable data: serializer fields, employee-name join) → Task 3.
- §5 (nav gating, two labels on one route) → Task 6.
- §6 (page redesign: employee picker, role descriptions, confirmation copy, approvals queue) → Tasks 7-10.
- §7 (testing, both backend and frontend) → covered throughout every task.
- Non-goals (§2 of spec: self-grant constraint untouched, Recruiter auto-approve untouched, no generic permission tool, no User/Employee merge) → no task touches the `CHECK` constraints, `RECRUITER` auto-approve branch, or adds a name field to `User`; employee name is joined for display only (`get_subject_name`/`get_employee_name`), never copied onto `User`.

**Placeholder scan:** an earlier draft of this plan had Task 8 write a placeholder (`ROLE_OPTIONS`, a stub `listAssignedRolesFallback`) and fix it up in the same step — caught on self-review and restructured into Task 7 (build the missing `/api/roles/` endpoint first) followed by Task 8 (write `GrantAccessForm` once, correctly, against the real endpoint). No placeholders remain in the current version.

**Type consistency:** `RoleGrantRequestRecord`'s new fields (Task 5) match what `RoleGrantRequestSerializer` emits (Task 3) and what `GrantAccessForm`/`AccessApprovalsQueue` consume (Tasks 8-9) — `requester_email`, `subject_email`, `subject_name`, `role_name` used identically throughout. `UserAccount.employee_name` (Task 5) matches `UserAdminSerializer.employee_name` (Task 3) and `GrantAccessForm`'s picker (Task 8). `listAssignedRoles` (Task 7) returns `{id, name}[]`, matching `AssignedRolesListView`'s response shape (Task 7) exactly.
