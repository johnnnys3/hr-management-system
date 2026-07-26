import { expect, test } from '@playwright/test'
import { loginAs } from '../helpers/auth'

// SRS §4.2: Create Job Requisition, Move Candidate to Offer Stage.
test.describe('Recruitment (SRS §4.2)', () => {
  test('Recruiter creates a requisition with an approval status (HRMS-FR-014)', async ({ page, context, baseURL }) => {
    await loginAs(context, baseURL!, 'e2e.recruiter@example.com', 'E2eTestpass123!')

    await page.goto('/recruitment')
    await page.getByRole('button', { name: 'New Requisition' }).click()
    await page.getByLabel('Department').click()
    await page.locator('.ant-select-item-option[title="E2E Engineering"]').click()
    await page.getByLabel('Job Title').click()
    await page.locator('.ant-select-item-option[title="E2E Engineer"]').click()
    await page.getByRole('dialog').getByRole('button', { name: 'Create' }).click()

    await expect(page.getByText('draft').first()).toBeVisible()
  })

  test('Recruiter moves a candidate to the offer stage and an offer letter exists (HRMS-FR-020)', async ({ page, context, baseURL }) => {
    // Multi-actor: Recruiter creates and drives the requisition/posting/
    // candidate/application; HR Administrator approves the requisition
    // (docs/07-iam-rbac.md §4.2 — requisition approval is HR
    // Administrator's, not the Recruiter's own action).
    const postingTitle = `E2E Backend Engineer ${Date.now()}`
    await loginAs(context, baseURL!, 'e2e.recruiter@example.com', 'E2eTestpass123!')
    await page.goto('/recruitment')

    await page.getByRole('button', { name: 'New Requisition' }).click()
    await page.getByLabel('Department').click()
    await page.locator('.ant-select-item-option[title="E2E Engineering"]').click()
    await page.getByLabel('Job Title').click()
    await page.locator('.ant-select-item-option[title="E2E Engineer"]').click()
    await page.getByRole('dialog').getByRole('button', { name: 'Create' }).click()
    await expect(page.getByText('draft').first()).toBeVisible()

    // A dedicated HR Administrator account, distinct from reports.spec.ts's
    // e2e.hra — different spec files run in parallel workers, and two
    // contexts authenticating as the same account concurrently race badly
    // enough to fail one or both tests.
    const hrAdminContext = await page.context().browser()!.newContext()
    await loginAs(hrAdminContext, baseURL!, 'e2e.hra2@example.com', 'E2eTestpass123!')
    const hrAdminPage = await hrAdminContext.newPage()
    await hrAdminPage.goto('/recruitment')
    await hrAdminPage.getByRole('button', { name: 'Approve' }).first().click()
    await expect(hrAdminPage.getByText('approved').first()).toBeVisible()
    await hrAdminContext.close()

    await page.reload()
    await page.getByRole('tab', { name: 'Postings' }).click()
    await page.getByRole('button', { name: 'New Posting' }).click()
    await page.getByLabel('Approved Requisition').click()
    await page.locator('.ant-select-item-option').first().click()
    await page.getByLabel('Title').fill(postingTitle)
    await page.getByLabel('Description').fill('Build things.')
    await page.getByLabel('Channel').click()
    await page.locator('.ant-select-item-option[title="External"]').click()
    await page.getByRole('dialog').getByRole('button', { name: 'Create' }).click()
    await expect(page.getByText(postingTitle)).toBeVisible()

    await page.getByRole('tab', { name: 'Candidates' }).click()
    await page.getByRole('button', { name: 'New Candidate' }).click()
    const candidateEmail = `e2e.candidate.${Date.now()}@example.com`
    await page.getByLabel('First Name').fill('Grace')
    await page.getByLabel('Last Name').fill('Hopper')
    await page.getByLabel('Email').fill(candidateEmail)
    await page.getByRole('dialog').getByRole('button', { name: 'Create' }).click()

    await expect(page).toHaveURL(/\/recruitment\/candidates\/\d+/)
    await page.getByRole('button', { name: 'New Application' }).click()
    await page.locator('.ant-select-input').click()
    await page.locator(`.ant-select-item-option[title="${postingTitle}"]`).click()
    await page.getByRole('dialog').getByRole('button', { name: 'Create' }).click()
    await expect(page.getByRole('cell', { name: 'applied' })).toBeVisible()
    await page.locator('.ant-table-row-expand-icon').click()

    await page.getByRole('button', { name: 'Issue Offer' }).click()
    await page.getByPlaceholder('Offered salary').fill('95000')
    await page.getByRole('dialog').getByRole('button', { name: 'Issue' }).click()

    await expect(page.getByText('pending', { exact: true })).toBeVisible()
    await page.reload()
    await expect(page.getByRole('cell', { name: 'offer', exact: true })).toBeVisible()
  })
})
