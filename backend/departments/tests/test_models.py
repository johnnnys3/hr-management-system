"""`department` and `job_title`, `docs/05-database-schema.md` §4.5."""
from django.db import IntegrityError, transaction
from django.test import TestCase

from departments.models import Department, JobTitle


class DepartmentModelTests(TestCase):
    def test_str_returns_the_name(self):
        department = Department.objects.create(name='Engineering')

        self.assertEqual(str(department), 'Engineering')

    def test_is_active_defaults_to_true(self):
        department = Department.objects.create(name='Engineering')

        self.assertTrue(department.is_active)

    def test_created_at_and_updated_at_are_set_automatically(self):
        department = Department.objects.create(name='Engineering')

        self.assertIsNotNone(department.created_at)
        self.assertIsNotNone(department.updated_at)

    def test_updated_at_advances_on_save(self):
        department = Department.objects.create(name='Engineering')
        original_updated_at = department.updated_at

        department.name = 'Engineering & Product'
        department.save()

        self.assertGreater(department.updated_at, original_updated_at)

    def test_name_must_be_unique(self):
        Department.objects.create(name='Engineering')

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Department.objects.create(name='Engineering')


class JobTitleModelTests(TestCase):
    def test_str_returns_the_name(self):
        job_title = JobTitle.objects.create(name='Software Engineer')

        self.assertEqual(str(job_title), 'Software Engineer')

    def test_is_active_defaults_to_true(self):
        job_title = JobTitle.objects.create(name='Software Engineer')

        self.assertTrue(job_title.is_active)

    def test_created_at_and_updated_at_are_set_automatically(self):
        job_title = JobTitle.objects.create(name='Software Engineer')

        self.assertIsNotNone(job_title.created_at)
        self.assertIsNotNone(job_title.updated_at)

    def test_updated_at_advances_on_save(self):
        job_title = JobTitle.objects.create(name='Software Engineer')
        original_updated_at = job_title.updated_at

        job_title.name = 'Senior Software Engineer'
        job_title.save()

        self.assertGreater(job_title.updated_at, original_updated_at)

    def test_name_must_be_unique(self):
        JobTitle.objects.create(name='Software Engineer')

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                JobTitle.objects.create(name='Software Engineer')