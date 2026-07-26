import { expect, test } from '@playwright/test'
import { loginAs } from '../helpers/auth'

// SRS §4.5: Generate Headcount Report.
test('HR Administrator opens Reporting, applies a department filter, and sees headcount (HRMS-FR-053, HRMS-FR-054)', async ({ page, context, baseURL }) => {
  await loginAs(context, baseURL!, 'e2e.hra@example.com', 'E2eTestpass123!')

  await page.goto('/reports')
  await expect(page.getByText('Total Headcount')).toBeVisible()

  await page.locator('.ant-select-input').click()
  await page.locator('.ant-select-item-option[title="E2E Engineering"]').click()

  await expect(page.getByText('Headcount by Department')).toBeVisible()
})
