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
  it('returns My Work and Admin (Role Grant Requests only) for a plain employee', () => {
    const groups = buildNavGroups(makeMe())
    expect(groups.map((g) => g.label)).toEqual(['My Work', 'Admin'])
    expect(groups[0].items.map((i) => i.key)).toEqual(['/', '/notifications', '/leave', '/my-profile'])
    expect(groups[1].items.map((i) => i.key)).toEqual(['/role-grant-requests'])
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

  it('adds Users and Audit Log to Admin for System Administrator, alongside Role Grant Requests', () => {
    const groups = buildNavGroups(makeMe({ groups: ['System Administrator'] }))
    const admin = groups.find((g) => g.label === 'Admin')
    expect(admin?.items.map((i) => i.key)).toEqual(['/role-grant-requests', '/users', '/audit-log'])
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
