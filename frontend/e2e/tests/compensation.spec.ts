import { expect, test } from '@playwright/test'
import { loginAs } from '../helpers/auth'

// SRS §4.6: Assign Employee to Pay Grade.
test('HR Officer assigns an employee to a pay grade and compensation history is stored (§5.3 append-only rule)', async ({ page, context, baseURL }) => {
  await loginAs(context, baseURL!, 'e2e.hro@example.com', 'E2eTestpass123!')

  await page.goto('/employees')
  await page.getByRole('cell', { name: 'Target', exact: true }).click()
  await page.getByRole('tab', { name: 'Compensation' }).click()

  await page.getByRole('button', { name: 'Assign Pay Grade' }).click()
  await page.getByLabel('Pay Grade', { exact: true }).click()
  await page.locator('.ant-select-item-option[title="E2E Grade 1"]').click()
  await page.getByLabel('Base Salary').fill('3500')
  await page.getByLabel('Effective From').fill('2027-02-01')
  await page.getByLabel('Effective From').press('Enter')
  await page.getByRole('dialog').getByRole('button', { name: 'Assign' }).click()

  await expect(page.getByRole('cell', { name: 'E2E Grade 1' })).toBeVisible()
  await expect(page.getByText('Current', { exact: true }).first()).toBeVisible()
})
