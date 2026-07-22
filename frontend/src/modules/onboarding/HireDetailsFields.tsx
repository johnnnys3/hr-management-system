import { DatePicker, Form, Input, Select } from 'antd'
import { useDepartments, useJobTitles } from '../departments/hooks'

export function HireDetailsFields({ includeName }: { includeName: boolean; grid?: boolean }) {
  const { data: departments = [] } = useDepartments()
  const { data: jobTitles = [] } = useJobTitles()

  return (
    <>
      <Form.Item label="Employee Number" name="employee_number" rules={[{ required: true }]}>
        <Input />
      </Form.Item>
      <Form.Item label="Hire Date" name="hire_date" rules={[{ required: true }]}>
        <DatePicker style={{ width: '100%' }} />
      </Form.Item>
      {includeName && (
        <>
          <Form.Item label="First Name" name="first_name" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item label="Department" name="department" rules={[{ required: true }]}>
            <Select options={departments.map((d) => ({ label: d.name, value: d.id }))} />
          </Form.Item>
          <Form.Item label="Last Name" name="last_name" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item label="Job Title" name="job_title" rules={[{ required: true }]}>
            <Select options={jobTitles.map((j) => ({ label: j.name, value: j.id }))} />
          </Form.Item>
        </>
      )}
      {!includeName && (
        <>
          <Form.Item label="Department" name="department" rules={[{ required: true }]}>
            <Select options={departments.map((d) => ({ label: d.name, value: d.id }))} />
          </Form.Item>
          <Form.Item label="Job Title" name="job_title" rules={[{ required: true }]}>
            <Select options={jobTitles.map((j) => ({ label: j.name, value: j.id }))} />
          </Form.Item>
        </>
      )}
      <Form.Item label="Date of Birth" name="date_of_birth" rules={[{ required: true }]}>
        <DatePicker style={{ width: '100%' }} />
      </Form.Item>
    </>
  )
}
