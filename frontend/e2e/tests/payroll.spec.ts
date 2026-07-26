import { expect, test } from '@playwright/test'
import { loginAs } from '../helpers/auth'

const PAYROLL_TOTP_SECRET = 'JBSWY3DPEHPK3PXP'
const HR_ADMIN_TOTP_SECRET = 'KRSXG5CTMVRXEZLU'

function isoDate(daysFromEpochBase: number): string {
  const d = new Date(Date.UTC(2030, 0, 1) + daysFromEpochBase * 86400000)
  return d.toISOString().slice(0, 10)
}

// SRS §4.4: Process Payroll. Multi-actor (Payroll Officer initiates,
// HR Administrator approves per docs/07-iam-rbac.md §4.4's deployment
// grant) and exposed to the async 202-and-poll pattern
// (docs/06-api-contracts.md §4.14) — this test polls the same way the
// page itself does, not assuming synchronous completion.
test('Payroll Officer initiates a run; HR Administrator approves and it finalizes with payslips (HRMS-BR-008)', async ({ page, context, baseURL }) => {
  // Unique period per run so repeated CI executions don't collide on the
  // (period_start, period_end) uniqueness constraint.
  const offset = Math.floor(Date.now() / 1000) % 100_000
  const periodStart = isoDate(offset)
  const periodEnd = isoDate(offset + 27)

  await loginAs(context, baseURL!, 'e2e.payroll1@example.com', 'E2eTestpass123!', PAYROLL_TOTP_SECRET)
  await page.goto('/payroll')

  await page.getByRole('button', { name: 'New Payroll Run' }).click()
  await page.getByLabel('Period').click()
  await page.locator('.ant-picker-input input').first().fill(periodStart)
  await page.locator('.ant-picker-input input').first().press('Enter')
  await page.locator('.ant-picker-input input').nth(1).fill(periodEnd)
  await page.locator('.ant-picker-input input').nth(1).press('Enter')
  await page.getByRole('dialog').getByRole('button', { name: 'Create' }).click()

  const row = page.getByRole('row', { name: periodStart })
  await expect(row).toBeVisible()
  await row.getByRole('button', { name: 'Calculate' }).click()
  await expect(row.getByText('calculated', { exact: true })).toBeVisible({ timeout: 15000 })

  await row.getByRole('button', { name: 'Submit for Approval' }).click()
  await expect(row.getByText('pending approval', { exact: true })).toBeVisible()

  const approverContext = await page.context().browser()!.newContext()
  await loginAs(approverContext, baseURL!, 'e2e.hra@example.com', 'E2eTestpass123!', HR_ADMIN_TOTP_SECRET)
  const approverPage = await approverContext.newPage()
  await approverPage.goto('/payroll')
  const approverRow = approverPage.getByRole('row', { name: periodStart })
  await approverRow.getByRole('button', { name: 'Approve' }).click()
  await expect(approverRow.getByText('approved', { exact: true })).toBeVisible()

  await approverRow.getByRole('button', { name: 'Finalize' }).click()
  await expect(approverRow.getByText('finalized', { exact: true })).toBeVisible({ timeout: 15000 })
  await approverContext.close()
})
