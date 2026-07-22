import { DatePicker, Form, Input, Select } from 'antd'
import { useDepartments, useJobTitles } from '../departments/hooks'

// Visual order for the two-column grid layout (design: Onboarding v2), independent
// of DOM order — CSS `order` lets the grid match the design's row pairing
// (Employee Number/Hire Date, First Name/Department, Last Name/Job Title, DOB)
// without reordering the underlying form fields.
const GRID_ORDER: Record<string, number> = {
  employee_number: 0,
  hire_date: 1,
  first_name: 2,
  department: 3,
  last_name: 4,
  job_title: 5,
  date_of_birth: 6,
}

export function HireDetailsFields({ includeName, grid }: { includeName: boolean; grid?: boolean }) {
  const { data: departments = [] } = useDepartments()
  const { data: jobTitles = [] } = useJobTitles()
  const order = (name: string) => (grid ? { style: { order: GRID_ORDER[name] } } : {})

  return (
    <>
      <Form.Item label="Employee Number" name="employee_number" rules={[{ required: true }]} {...order('employee_number')}>
        <Input />
      </Form.Item>
      {includeName && (
        <>
          <Form.Item label="First Name" name="first_name" rules={[{ required: true }]} {...order('first_name')}>
            <Input />
          </Form.Item>
          <Form.Item label="Last Name" name="last_name" rules={[{ required: true }]} {...order('last_name')}>
            <Input />
          </Form.Item>
        </>
      )}
      <Form.Item label="Date of Birth" name="date_of_birth" rules={[{ required: true }]} {...order('date_of_birth')}>
        <DatePicker style={{ width: '100%' }} />
      </Form.Item>
      <Form.Item label="Hire Date" name="hire_date" rules={[{ required: true }]} {...order('hire_date')}>
        <DatePicker style={{ width: '100%' }} />
      </Form.Item>
      <Form.Item label="Department" name="department" rules={[{ required: true }]} {...order('department')}>
        <Select options={departments.map((d) => ({ label: d.name, value: d.id }))} />
      </Form.Item>
      <Form.Item label="Job Title" name="job_title" rules={[{ required: true }]} {...order('job_title')}>
        <Select options={jobTitles.map((j) => ({ label: j.name, value: j.id }))} />
      </Form.Item>
    </>
  )
}
