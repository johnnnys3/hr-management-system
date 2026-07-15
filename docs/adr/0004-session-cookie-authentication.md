# ADR-0004: Session cookie authentication rather than JWT

**Status:** Accepted
**Date:** 2026-07-15

## Context

ADR-0001 established a React SPA consuming a REST API. Common practice pairs SPA clients with bearer tokens, typically JWT held in browser storage. That pattern was evaluated against the specific requirements of this system and found unsuitable.

Three requirements bear directly on the choice:

- **HRMS-BR-012** — terminated, resigned, or retired employees shall not access the self-service portal unless explicitly permitted by policy.
- **HRMS-NFR-023** — sessions shall expire after a defined period of inactivity.
- **HRMS-NFR-022** — the system shall log login attempts, record changes, payroll actions, approvals, and permission changes.

The data under protection includes salary figures, SSNIT numbers, PAYE records, and identity documents.

## Decision

Authentication uses **Django server-side sessions with a cookie** carrying the session identifier. The cookie is set `HttpOnly`, `Secure`, and `SameSite=Lax`.

JWT is not used.

This decision requires the SPA and the API to be served from a single origin. See ADR-0009.

## Consequences

**Positive**

- **Immediate revocation.** HRMS-BR-012 requires that access ends when employment ends. Deleting the server-side session revokes access on the next request. A JWT remains valid until expiry regardless of account state; emulating revocation requires a server-side blocklist checked on every request, which forfeits the statelessness that motivates JWT in the first place.
- **Native inactivity expiry.** HRMS-NFR-023 is a server-side session setting. Achieving equivalent behaviour with JWT requires refresh token rotation and additional state.
- **Reduced token theft exposure.** An `HttpOnly` cookie is not readable by JavaScript. A JWT in browser storage is readable, and any cross-site scripting defect exposes it. Given the sensitivity of the data, the cookie is the stronger posture.
- **Simpler audit.** Session state is server-side, so HRMS-NFR-022 logging has a single natural location.

**Negative**

- **Same-origin constraint.** Cross-origin cookie delivery requires `SameSite=None; Secure` and is increasingly restricted by browser third-party cookie policy. This constrains deployment topology, as recorded in ADR-0009.
- **CSRF protection required.** Cookie-borne credentials are automatically attached by the browser, so state-changing endpoints require CSRF token verification. Django provides this; it must not be disabled for convenience.
- **Server-side session storage.** Sessions consume storage and must be cleaned up.

**Non-consequence**

JWT's principal advantages — stateless verification across independent services, and credentials shared across multiple client types — do not apply here. The backend is a single monolith (ADR-0001), there are no third-party API consumers, and a native mobile application is out of scope per SRS §6.4.

Should a native mobile client enter scope, this decision should be revisited rather than worked around.
