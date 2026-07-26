import { expect, test } from '@playwright/test'
import { loginAs } from '../helpers/auth'

// A dedicated HR Administrator account — payroll.spec.ts (e2e.hra) and
// recruitment.spec.ts (e2e.hra2) both need one concurrently too, and two
// contexts authenticating as the same TOTP-gated account in the same 30s
// window hit accounts/totp.py's anti-replay check.
const HR_ADMIN_3_TOTP_SECRET = 'ONSWG4TFOQYTEMZU'

// SRS §4.5: Generate Headcount Report.
test('HR Administrator opens Reporting, applies a department filter, and sees headcount (HRMS-FR-053, HRMS-FR-054)', async ({ page, context, baseURL }) => {
  await loginAs(context, baseURL!, 'e2e.hra3@example.com', 'E2eTestpass123!', HR_ADMIN_3_TOTP_SECRET)

  await page.goto('/reports')
  await expect(page.getByText('Total Headcount')).toBeVisible()

  await page.locator('.ant-select-input').click()
  await page.locator('.ant-select-item-option[title="E2E Engineering"]').click()

  await expect(page.getByText('Headcount by Department')).toBeVisible()
})
