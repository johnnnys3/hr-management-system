import { describe, expect, it } from 'vitest'
import { buildNavGroups } from './navGroups'
import type { Me } from '../api/types'

function makeMe(overrides: Partial<Me> = {}): Me {
  return {
    id: 1,
    email: 'a@b.com',
    groups: [],
    is_employee: true,
    is_manager: false,
    second_factor_enrollment_pending: false,
    ...overrides,
  }
}

describe('buildNavGroups', () => {
  it('shows only My Work for a plain employee (no Access item at all)', () => {
    const groups = buildNavGroups(makeMe())
    expect(groups.map((g) => g.label)).toEqual(['My Work'])
  })

  it('adds My Team to People for a manager', () => {
    const groups = buildNavGroups(makeMe({ is_manager: true }))
    const people = groups.find((g) => g.label === 'People')
    expect(people?.items.map((i) => i.key)).toEqual(['/my-team'])
  })

  it('adds Employees and Departments to People for HR Administrator, and Reports to Payroll & Compensation', () => {
    const groups = buildNavGroups(makeMe({ groups: ['HR Administrator'] }))
    const people = groups.find((g) => g.label === 'People')
    expect(people?.items.map((i) => i.key)).toEqual(expect.arrayContaining(['/departments', '/employees', '/recruitment']))
    const payroll = groups.find((g) => g.label === 'Payroll & Compensation')
    expect(payroll?.items.map((i) => i.key)).toEqual(expect.arrayContaining(['/compensation', '/reports']))
  })

  it('shows Grant Access (not Access Approvals) for System Administrator, alongside Users and Audit Log', () => {
    const groups = buildNavGroups(makeMe({ groups: ['System Administrator'] }))
    const admin = groups.find((g) => g.label === 'Admin')
    expect(admin?.items.map((i) => i.key)).toEqual(['/access', '/users', '/audit-log'])
    expect(admin?.items.find((i) => i.key === '/access')?.label).toEqual('Grant Access')
  })

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

  it('adds Payroll to Payroll & Compensation for Payroll Officer', () => {
    const groups = buildNavGroups(makeMe({ groups: ['Payroll Officer'] }))
    const payroll = groups.find((g) => g.label === 'Payroll & Compensation')
    expect(payroll?.items.map((i) => i.key)).toEqual(expect.arrayContaining(['/compensation', '/payroll', '/reports']))
  })

  it('omits People and Payroll & Compensation entirely when they have no visible items', () => {
    const groups = buildNavGroups(makeMe())
    expect(groups.find((g) => g.label === 'People')).toBeUndefined()
    expect(groups.find((g) => g.label === 'Payroll & Compensation')).toBeUndefined()
  })

  it('returns an empty array when me is null', () => {
    expect(buildNavGroups(null)).toEqual([])
  })

  it('carries an unread notification count onto the Notifications item when provided', () => {
    const groups = buildNavGroups(makeMe(), 3)
    const myWork = groups.find((g) => g.label === 'My Work')
    const notifications = myWork?.items.find((i) => i.key === '/notifications')
    expect(notifications?.badge).toBe(3)
  })
})
