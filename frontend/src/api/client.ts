export class ApiError extends Error {
  status: number
  code?: string
  fields?: Record<string, string[]>

  constructor(status: number, message: string, code?: string, fields?: Record<string, string[]>) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.code = code
    this.fields = fields
  }
}

export function getCsrfToken(): string | null {
  const match = document.cookie.match(/(?:^|; )csrftoken=([^;]+)/)
  return match ? decodeURIComponent(match[1]) : null
}

const UNSAFE_METHODS = new Set(['POST', 'PATCH', 'PUT', 'DELETE'])

interface ApiFetchOptions {
  method?: 'GET' | 'POST' | 'PATCH' | 'PUT' | 'DELETE'
  body?: unknown
}

export async function apiFetch<T = unknown>(path: string, options: ApiFetchOptions = {}): Promise<T> {
  const method = options.method ?? 'GET'
  const headers: Record<string, string> = {}

  if (options.body !== undefined) {
    headers['Content-Type'] = 'application/json'
  }
  if (UNSAFE_METHODS.has(method)) {
    const token = getCsrfToken()
    if (token) {
      headers['X-CSRFToken'] = token
    }
  }

  const response = await fetch(path, {
    method,
    headers,
    credentials: 'same-origin',
    body: options.body !== undefined ? JSON.stringify(options.body) : undefined,
  })

  if (response.status === 204) {
    return undefined as T
  }

  const text = await response.text()
  let data: any
  if (text) {
    try {
      data = JSON.parse(text)
    } catch {
      throw new ApiError(response.status, 'The server returned an unexpected response.', 'invalid_response')
    }
  }

  if (!response.ok) {
    const errorBody = data?.error
    const apiError = new ApiError(
      response.status,
      errorBody?.message ?? `Request failed with status ${response.status}`,
      errorBody?.code,
      errorBody?.fields,
    )

    // Global 401 redirect for authenticated requests (not /auth/me/ on app load)
    if (response.status === 401 && path !== '/api/auth/me/') {
      window.location.href = '/login'
    }

    throw apiError
  }

  return data as T
}
