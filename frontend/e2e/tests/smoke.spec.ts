import { expect, test } from '@playwright/test'
import { loginAs } from '../helpers/auth'

test('HR Officer can log in and reach the Employees page', async ({ page, context, baseURL }) => {
  await loginAs(context, baseURL!, 'e2e.hro@example.com', 'E2eTestpass123!')
  await page.goto('/employees')
  await expect(page.getByText('New Employee')).toBeVisible()
})
