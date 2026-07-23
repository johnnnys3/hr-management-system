import { expect, test } from '@playwright/test'
import { loginAs } from '../helpers/auth'

// SRS §4.3: Employee Updates Personal Details.
test('Employee updates an allowed field; a restricted field is rejected server-side (HRMS-FR-027)', async ({ page, context, baseURL }) => {
  await loginAs(context, baseURL!, 'e2e.employee@example.com', 'E2eTestpass123!')

  await page.goto('/my-profile')
  await page.getByLabel('First Name').fill('Grace')
  await page.getByRole('button', { name: 'Save' }).click()
  await expect(page.getByText('Profile updated.')).toBeVisible()

  // Restricted fields (salary, job title, department, status, manager) are
  // not rendered as editable inputs at all — client-side rejection is their
  // absence from the form. Forcing the same restriction past the client
  // (a direct PATCH naming employment_status) proves the server-side half:
  // the narrower self-service serializer marks it read-only, so the value
  // must be silently unchanged, not merely that the request "succeeds".
  const before = await page.request.get('/api/employees/me/')
  const beforeStatus = (await before.json()).employment_status

  const csrfCookie = (await context.cookies()).find((c) => c.name === 'csrftoken')
  const patch = await page.request.fetch('/api/employees/me/', {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfCookie?.value ?? '' },
    data: { employment_status: 'terminated' },
  })
  expect(patch.ok()).toBeTruthy()

  const after = await page.request.get('/api/employees/me/')
  expect((await after.json()).employment_status).toBe(beforeStatus)
})
