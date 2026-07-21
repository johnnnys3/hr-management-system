import { useMutation } from '@tanstack/react-query'
import { Button, DatePicker, Form, Input, Select, Typography, message } from 'antd'
import dayjs from 'dayjs'
import { useNavigate } from 'react-router-dom'
import { ApiError } from '../../api/client'
import { convertDirectHire } from '../../api/onboarding'
import { useDepartments, useJobTitles } from '../departments/hooks'

interface DirectHireFormValues {
  employee_number: string
  first_name: string
  last_name: string
  date_of_birth: dayjs.Dayjs
  hire_date: dayjs.Dayjs
  department: number
  job_title: number
}

export function OnboardingPage() {
  const navigate = useNavigate()
  const [form] = Form.useForm<DirectHireFormValues>()
  const { data: departments = [] } = useDepartments()
  const { data: jobTitles = [] } = useJobTitles()

  const mutation = useMutation({
    mutationFn: (values: DirectHireFormValues) =>
      convertDirectHire({
        employee_number: values.employee_number,
        first_name: values.first_name,
        last_name: values.last_name,
        date_of_birth: values.date_of_birth.format('YYYY-MM-DD'),
        hire_date: values.hire_date.format('YYYY-MM-DD'),
        department: values.department,
        job_title: values.job_title,
      }),
    onSuccess: (checklist) => navigate(`/onboarding/${checklist.id}`),
    onError: (e) => message.error(e instanceof ApiError ? e.message : 'Conversion failed.'),
  })

  return (
    <div style={{ maxWidth: 480 }}>
      <Typography.Title level={3}>New Direct Hire</Typography.Title>
      <Typography.Paragraph type="secondary">
        Creates the employee record and starts an onboarding checklist. To hire from a recruitment application
        instead, use the Convert to Employee action on the candidate's offer.
      </Typography.Paragraph>
      <Form form={form} layout="vertical" onFinish={(values) => mutation.mutate(values)}>
        <Form.Item label="Employee Number" name="employee_number" rules={[{ required: true }]}>
          <Input />
        </Form.Item>
        <Form.Item label="First Name" name="first_name" rules={[{ required: true }]}>
          <Input />
        </Form.Item>
        <Form.Item label="Last Name" name="last_name" rules={[{ required: true }]}>
          <Input />
        </Form.Item>
        <Form.Item label="Date of Birth" name="date_of_birth" rules={[{ required: true }]}>
          <DatePicker style={{ width: '100%' }} />
        </Form.Item>
        <Form.Item label="Hire Date" name="hire_date" rules={[{ required: true }]}>
          <DatePicker style={{ width: '100%' }} />
        </Form.Item>
        <Form.Item label="Department" name="department" rules={[{ required: true }]}>
          <Select options={departments.map((d) => ({ label: d.name, value: d.id }))} />
        </Form.Item>
        <Form.Item label="Job Title" name="job_title" rules={[{ required: true }]}>
          <Select options={jobTitles.map((j) => ({ label: j.name, value: j.id }))} />
        </Form.Item>
        <Button type="primary" htmlType="submit" loading={mutation.isPending}>
          Convert
        </Button>
      </Form>
    </div>
  )
}
