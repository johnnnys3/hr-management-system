from datetime import date

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from compensation.models import CompensationRecord
from departments.models import Department, JobTitle
from employees.models import Employee

User = get_user_model()


def user_with_role(email, role_name, employee=None):
    user = User.objects.create_user(email=email, password='x', employee=employee)
    if role_name:
        user.groups.add(Group.objects.get(name=role_name))
    return user


def make_employee(number, first_name, last_name, employment_status=Employee.STATUS_ACTIVE):
    department = Department.objects.get_or_create(name='Engineering')[0]
    job_title = JobTitle.objects.get_or_create(name='Engineer')[0]
    return Employee.objects.create(
        employee_number=number, first_name=first_name, last_name=last_name,
        date_of_birth='1990-01-01', department=department, job_title=job_title,
        hire_date=date.today(), employment_status=employment_status,
    )


def give_compensation(employee, base_salary='1500.00', effective_from='2026-01-01'):
    return CompensationRecord.objects.create(
        employee=employee, base_salary=base_salary, effective_from=effective_from,
    )
