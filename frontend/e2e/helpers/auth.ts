import type { BrowserContext } from '@playwright/test'
import { generateTotpCode } from './totp'

function cookieValue(setCookieHeaders: { name: string; value: string }[], cookieName: string): string | undefined {
  const header = setCookieHeaders.find((h) => h.value.startsWith(`${cookieName}=`))
  return header?.value.split(';')[0].split('=')[1]
}

/**
 * Logs in via the real API (no browser form) and injects the resulting
 * session and CSRF cookies into the browser context.
 *
 * Real-browser form login is blocked in this environment: `DJANGO_DEBUG=false`
 * forces `Secure` on both cookies, but Caddy serves plain HTTP locally and in
 * CI (`auto_https off`), so a browser refuses to attach either on a
 * subsequent plain-HTTP request. This is the same workaround used ad hoc via
 * `curl` in earlier sessions, made repeatable: fetch the CSRF cookie, POST
 * login with it, then re-add both cookies via `addCookies` with
 * `secure: false` so they round-trip over plain HTTP for the rest of the
 * test. Never do this against a real deployment — it exists only because
 * this stack is deliberately unencrypted for local/CI use.
 */
export async function loginAs(
  context: BrowserContext,
  baseURL: string,
  email: string,
  password: string,
  totpSecret?: string,
): Promise<void> {
  const csrfResponse = await context.request.get(`${baseURL}/api/auth/csrf/`)
  const csrfSetCookies = csrfResponse.headersArray().filter((h) => h.name.toLowerCase() === 'set-cookie')
  const csrfToken = cookieValue(csrfSetCookies, 'csrftoken')
  if (!csrfToken) {
    throw new Error('E2E CSRF bootstrap returned no csrftoken cookie')
  }

  const loginResponse = await context.request.post(`${baseURL}/api/auth/login/`, {
    data: totpSecret ? { email, password, totp_code: generateTotpCode(totpSecret) } : { email, password },
    headers: { 'Content-Type': 'application/json', Cookie: `csrftoken=${csrfToken}`, 'X-CSRFToken': csrfToken },
  })
  if (!loginResponse.ok()) {
    throw new Error(`E2E login failed for ${email}: ${loginResponse.status()} ${await loginResponse.text()}`)
  }

  const loginSetCookies = loginResponse.headersArray().filter((h) => h.name.toLowerCase() === 'set-cookie')
  const sessionValue = cookieValue(loginSetCookies, 'sessionid')
  const freshCsrfValue = cookieValue(loginSetCookies, 'csrftoken') ?? csrfToken
  if (!sessionValue) {
    throw new Error(`E2E login for ${email} returned no sessionid cookie`)
  }

  const domain = new URL(baseURL).hostname
  await context.addCookies([
    { name: 'sessionid', value: sessionValue, domain, path: '/', httpOnly: true, secure: false, sameSite: 'Lax' },
    { name: 'csrftoken', value: freshCsrfValue, domain, path: '/', httpOnly: false, secure: false, sameSite: 'Lax' },
  ])
}
