import { expect, test } from '@playwright/test'
import { loginAs } from '../helpers/auth'

// SRS §4.1: Create Employee Record, Update Employee Record.
test.describe('Employee records (SRS §4.1)', () => {
  test.beforeEach(async ({ context, baseURL }) => {
    await loginAs(context, baseURL!, 'e2e.hro@example.com', 'E2eTestpass123!')
  })

  test('HR Officer creates an employee record with a unique employee ID (HRMS-BR-001)', async ({ page }) => {
    const employeeNumber = `E2E-CREATE-${Date.now()}`

    await page.goto('/employees')
    await page.getByRole('button', { name: 'New Employee' }).click()

    await page.getByLabel('Employee Number').fill(employeeNumber)
    await page.getByLabel('First Name').fill('Ada')
    await page.getByLabel('Last Name').fill('Lovelace')
    await page.getByLabel('Date of Birth').fill('1990-01-01')
    await page.getByLabel('Date of Birth').press('Enter')
    await page.getByLabel('Hire Date').fill('2024-01-01')
    await page.getByLabel('Hire Date').press('Enter')
    await page.getByLabel('Department').click()
    await page.locator('.ant-select-item-option[title="E2E Engineering"]').click()
    await page.getByLabel('Job Title').click()
    await page.locator('.ant-select-item-option[title="E2E Engineer"]').click()

    await page.getByRole('dialog').getByRole('button', { name: 'Create' }).click()

    // Create navigates to /employees/{id} — wait for that first, rather
    // than asserting the field directly, so a slower CI runner's extra
    // navigation latency doesn't race the assertion's own timeout.
    await expect(page).toHaveURL(/\/employees\/\d+/)
    // The Employee Number field has no `name` prop (it's display-only),
    // so antd never sets a `for` attribute on its label — getByLabel
    // can't resolve it. Located structurally instead.
    await expect(
      page.locator('.ant-form-item', { hasText: 'Employee Number' }).locator('input'),
    ).toHaveValue(employeeNumber)
  })

  test('HR Officer updates employment status and employment_history carries the change (HRMS-FR-010)', async ({ page }) => {
    await page.goto('/employees')
    await page.getByRole('cell', { name: 'Target', exact: true }).click()

    await page.getByLabel('Employment Status').click()
    await page.locator('.ant-select-item-option[title="on leave"]').click()
    await page.getByRole('button', { name: 'Save' }).click()
    await expect(page.getByText('Saved.')).toBeVisible()

    await page.getByRole('tab', { name: 'Employment History' }).click()
    await expect(page.getByText('status change').first()).toBeVisible()

    // Reset for test re-runs against the same seeded fixture.
    await page.getByRole('tab', { name: 'Profile' }).click()
    await page.getByLabel('Employment Status').click()
    await page.locator('.ant-select-item-option[title="active"]').click()
    await page.getByRole('button', { name: 'Save' }).click()
  })
})
