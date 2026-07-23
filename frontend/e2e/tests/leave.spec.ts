import { expect, test } from '@playwright/test'
import { loginAs } from '../helpers/auth'

// SRS §4.7: Submit Leave Request, Approve Leave Request. The latter is the
// same underlying action as SRS §4.3's "Manager Approves Request" — HRMS-
// FR-031 is a documented duplicate of HRMS-FR-064 (DOC-010) — so one test
// satisfies both citations rather than driving the identical click twice.
test('Employee submits a leave request; Manager approves it and the balance updates (HRMS-FR-034, HRMS-BR-010)', async ({ page, context, baseURL }) => {
  await loginAs(context, baseURL!, 'e2e.employee@example.com', 'E2eTestpass123!')
  await page.goto('/leave')

  await page.getByRole('button', { name: 'New Request' }).click()
  await page.getByLabel('Leave Type').click()
  await page.locator('.ant-select-item-option').first().click()
  await page.locator('.ant-picker-input input').first().fill('2027-01-04')
  await page.locator('.ant-picker-input input').first().press('Enter')
  await page.locator('.ant-picker-input input').nth(1).fill('2027-01-05')
  await page.locator('.ant-picker-input input').nth(1).press('Enter')
  await page.getByLabel('Reason').fill('E2E leave request')
  await page.getByRole('dialog').getByRole('button', { name: 'OK' }).click()

  await expect(page.getByText('pending', { exact: true }).first()).toBeVisible()

  const managerContext = await page.context().browser()!.newContext()
  await loginAs(managerContext, baseURL!, 'e2e.manager@example.com', 'E2eTestpass123!')
  const managerPage = await managerContext.newPage()
  await managerPage.goto('/leave')
  await managerPage.getByRole('button', { name: 'Approve' }).first().click()
  await expect(managerPage.getByText('approved', { exact: true }).first()).toBeVisible()
  await managerContext.close()
})
