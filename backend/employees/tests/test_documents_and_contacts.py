"""`/api/employees/{id}/documents/`, `/api/employees/{id}/emergency-contacts/`,
`docs/06-api-contracts.md` §4.3."""
from datetime import date

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase

from departments.models import Department, JobTitle
from employees.models import EmergencyContact, Employee, EmployeeDocument
from iam.roles import HR_ADMINISTRATOR, HR_OFFICER

User = get_user_model()

PDF_BYTES = b'%PDF-1.4 fake pdf content'


def _user_with_role(email, role_name):
    user = User.objects.create_user(email=email, password='x')
    user.groups.add(Group.objects.get(name=role_name))
    return user


class EmployeeDocumentTests(APITestCase):
    def setUp(self):
        self.hr_officer = _user_with_role('hrofficer@example.com', HR_OFFICER)
        self.hr_admin = _user_with_role('hradmin@example.com', HR_ADMINISTRATOR)
        department = Department.objects.create(name='Engineering')
        job_title = JobTitle.objects.create(name='Engineer')
        self.employee = Employee.objects.create(
            employee_number='E-1', first_name='Ada', last_name='Lovelace',
            date_of_birth='1990-01-01', department=department, job_title=job_title,
            hire_date=date.today(),
        )
        self.url = f'/api/employees/{self.employee.pk}/documents/'

    def test_hr_officer_can_upload_a_document(self):
        self.client.force_authenticate(self.hr_officer)
        upload = SimpleUploadedFile('contract.pdf', PDF_BYTES, content_type='application/pdf')

        response = self.client.post(self.url, {'file': upload, 'document_type': 'contract'}, format='multipart')

        self.assertEqual(response.status_code, 201)
        document = EmployeeDocument.objects.get(employee=self.employee)
        self.assertEqual(document.content_type, 'application/pdf')
        self.assertNotEqual(document.object_key, 'contract.pdf')
        self.assertEqual(document.file_name, 'contract.pdf')

    def test_hr_administrator_cannot_upload_a_document(self):
        self.client.force_authenticate(self.hr_admin)
        upload = SimpleUploadedFile('contract.pdf', PDF_BYTES, content_type='application/pdf')

        response = self.client.post(self.url, {'file': upload, 'document_type': 'contract'}, format='multipart')

        self.assertEqual(response.status_code, 403)

    def test_unrecognised_file_type_is_rejected(self):
        self.client.force_authenticate(self.hr_officer)
        upload = SimpleUploadedFile('script.exe', b'MZ-not-a-real-document', content_type='application/pdf')

        response = self.client.post(self.url, {'file': upload, 'document_type': 'contract'}, format='multipart')

        self.assertEqual(response.status_code, 400)

    def test_content_type_is_derived_from_inspection_not_client_header(self):
        self.client.force_authenticate(self.hr_officer)
        upload = SimpleUploadedFile('contract.pdf', PDF_BYTES, content_type='text/plain')

        response = self.client.post(self.url, {'file': upload, 'document_type': 'contract'}, format='multipart')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['content_type'], 'application/pdf')

    def test_employee_can_read_own_documents(self):
        EmployeeDocument.objects.create(
            employee=self.employee, document_type='contract', object_key='k1',
            file_name='c.pdf', content_type='application/pdf', size_bytes=10,
        )
        user = User.objects.create_user(email='ada@example.com', password='x', employee=self.employee)
        self.client.force_authenticate(user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)


class EmergencyContactTests(APITestCase):
    def setUp(self):
        self.hr_officer = _user_with_role('hrofficer@example.com', HR_OFFICER)
        department = Department.objects.create(name='Engineering')
        job_title = JobTitle.objects.create(name='Engineer')
        self.employee = Employee.objects.create(
            employee_number='E-1', first_name='Ada', last_name='Lovelace',
            date_of_birth='1990-01-01', department=department, job_title=job_title,
            hire_date=date.today(),
        )
        self.url = f'/api/employees/{self.employee.pk}/emergency-contacts/'

    def test_hr_officer_can_create_and_update_a_contact(self):
        self.client.force_authenticate(self.hr_officer)

        create_response = self.client.post(self.url, {
            'name': 'Grace Hopper', 'relationship': 'Sister', 'phone': '555-0100',
        })
        self.assertEqual(create_response.status_code, 201)
        contact_id = create_response.data['id']

        patch_response = self.client.patch(f'{self.url}{contact_id}/', {'is_primary': True})
        self.assertEqual(patch_response.status_code, 200)
        self.assertTrue(EmergencyContact.objects.get(pk=contact_id).is_primary)

    def test_employee_cannot_create_a_contact(self):
        user = User.objects.create_user(email='ada@example.com', password='x', employee=self.employee)
        self.client.force_authenticate(user)

        response = self.client.post(self.url, {'name': 'Grace Hopper', 'relationship': 'Sister', 'phone': '555-0100'})

        self.assertEqual(response.status_code, 403)
