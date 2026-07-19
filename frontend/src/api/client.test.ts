import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { ApiError, apiFetch, getCsrfToken } from './client'

describe('getCsrfToken', () => {
  afterEach(() => {
    document.cookie = 'csrftoken=; expires=Thu, 01 Jan 1970 00:00:00 GMT'
  })

  it('reads the csrftoken cookie', () => {
    document.cookie = 'csrftoken=abc123'
    expect(getCsrfToken()).toBe('abc123')
  })

  it('returns null when no csrftoken cookie is set', () => {
    expect(getCsrfToken()).toBeNull()
  })
})

describe('apiFetch', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn())
  })

  afterEach(() => {
    vi.unstubAllGlobals()
    document.cookie = 'csrftoken=; expires=Thu, 01 Jan 1970 00:00:00 GMT'
  })

  it('sends the CSRF header on POST when a csrftoken cookie exists', async () => {
    document.cookie = 'csrftoken=tok-1'
    vi.mocked(fetch).mockResolvedValue(
      new Response(JSON.stringify({ ok: true }), { status: 200 }),
    )

    await apiFetch('/api/auth/login/', { method: 'POST', body: { email: 'a@b.com' } })

    const [, init] = vi.mocked(fetch).mock.calls[0]
    expect((init?.headers as Record<string, string>)['X-CSRFToken']).toBe('tok-1')
  })

  it('does not send a CSRF header on GET', async () => {
    document.cookie = 'csrftoken=tok-1'
    vi.mocked(fetch).mockResolvedValue(new Response(JSON.stringify({}), { status: 200 }))

    await apiFetch('/api/auth/me/')

    const [, init] = vi.mocked(fetch).mock.calls[0]
    expect((init?.headers as Record<string, string> | undefined)?.['X-CSRFToken']).toBeUndefined()
  })

  it('parses the uniform error envelope and throws ApiError', async () => {
    vi.mocked(fetch).mockResolvedValue(
      new Response(
        JSON.stringify({ error: { code: 'validation_error', message: 'Bad input.', fields: { email: ['Required.'] } } }),
        { status: 400 },
      ),
    )

    await expect(apiFetch('/api/auth/login/', { method: 'POST', body: {} })).rejects.toMatchObject({
      status: 400,
      code: 'validation_error',
      message: 'Bad input.',
      fields: { email: ['Required.'] },
    })
  })

  it('throws ApiError with status only for a non-JSON error body (e.g. 204/401 with no body)', async () => {
    vi.mocked(fetch).mockResolvedValue(new Response(null, { status: 401 }))

    await expect(apiFetch('/api/auth/me/')).rejects.toBeInstanceOf(ApiError)
  })

  it('returns undefined for a 204 No Content success response', async () => {
    vi.mocked(fetch).mockResolvedValue(new Response(null, { status: 204 }))

    const result = await apiFetch('/api/auth/logout/', { method: 'POST' })
    expect(result).toBeUndefined()
  })
})
