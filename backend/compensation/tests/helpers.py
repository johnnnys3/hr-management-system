from datetime import date

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from departments.models import Department, JobTitle
from employees.models import Employee

from ..models import PayGrade, SalaryStructure

User = get_user_model()


def user_with_role(email, role_name, employee=None):
    user = User.objects.create_user(email=email, password='x', employee=employee)
    user.groups.add(Group.objects.get(name=role_name))
    return user


def make_employee(number, first_name, last_name):
    department = Department.objects.get_or_create(name='Engineering')[0]
    job_title = JobTitle.objects.get_or_create(name='Engineer')[0]
    return Employee.objects.create(
        employee_number=number, first_name=first_name, last_name=last_name,
        date_of_birth='1990-01-01', department=department, job_title=job_title, hire_date=date.today(),
    )


def make_pay_grade(name='Grade 1', min_salary='1000.00', max_salary='2000.00'):
    structure = SalaryStructure.objects.get_or_create(
        name='Default structure', defaults={'effective_from': date.today()}
    )[0]
    return PayGrade.objects.create(
        salary_structure=structure, name=name, min_salary=min_salary, max_salary=max_salary,
    )
