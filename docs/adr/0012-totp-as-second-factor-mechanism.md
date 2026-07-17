# ADR-0012: TOTP as the second-factor mechanism

**Status:** Accepted
**Date:** 2026-07-17

## Context

HRMS-NFR-024 (SRS v1.1, a *shall*) requires multi-factor authentication for administrators and payroll users on every authentication. `docs/05-database-schema.md` §4.2 schemas a `second_factor` table with an opaque `secret_ref`, declining to name the cryptographic mechanism: "the cryptographic mechanism (TOTP, WebAuthn, or otherwise) is an implementation choice `docs/06-api-contracts.md` or a later ADR settles." `docs/06-api-contracts.md` restates the deferral and names the trade-off without adjudicating it: "TOTP's offline verifiability against WebAuthn's phishing resistance."

Module 3 (Authentication, `docs/02-project-plan.md` §6.1) is where that deferral is spent: 6 of its 8 days are HRMS-NFR-024 integration, enrolment, and presentation, and the mechanism must be fixed before any of that is built.

## Decision

**TOTP (RFC 6238).**

## Rationale

- **No offline fallback is otherwise available.** HRMS-NFR-024 requires that recovery of a lost second factor go through human approval (`docs/07-iam-rbac.md` §7.3, §8), not a technical bypass — the recovery path is already slow by design. WebAuthn's hardware/platform binding adds a second failure mode (lost device, no registered platform authenticator) on top of that same slow path with no compensating control. TOTP's shared-secret model lets a user re-derive codes from any authenticator app without device-specific enrolment loss.
- **No phishing threat model motivates the stronger property.** WebAuthn's principal advantage is phishing resistance against credential relay. This is an internal system (ADR-0001 monolith, ADR-0004 single-origin session cookies, no third-party API consumers) with no history of targeted phishing and no requirement naming that threat. Paying WebAuthn's client-support and enrolment cost for a property nothing in the SRS asks for is the same shape of over-implementation §6.1 of `docs/07-iam-rbac.md` declines elsewhere (there, enforcing a *should* as a *shall*).
- **Narrower client-support burden.** WebAuthn support varies by browser, platform authenticator availability, and — for roaming authenticators — hardware the organisation has not committed to provisioning (TBD-001 leaves the organisation undetermined). TOTP requires only an authenticator app, which every administrator and payroll user's personal or work phone already suffices for.
- **Simpler to build within the 6-day estimate.** TOTP is a shared-secret HMAC computation with no challenge-response ceremony, no relying-party origin binding, and no attestation. It fits the `secret_ref` column the schema already committed to (§4.2): `secret_ref` is the TOTP shared secret, encrypted at rest, never the raw value in application logs.

## Consequences

**Positive**

- Module 3's second-factor estimate can proceed against a fixed mechanism rather than a placeholder.
- `secret_ref` in `second_factor` (`docs/05-database-schema.md` §4.2) is now concretely the encrypted TOTP shared secret.
- Enrolment is a QR code (or manual entry of the secret) presented once to the account holder, per HRMS-NFR-024's requirement that enrolment be performed by the account holder and not by an administering role.

**Negative**

- **No phishing resistance.** A user who is socially engineered into reading a valid TOTP code to an attacker in real time is not protected. Accepted because no requirement or threat model in scope names this attack.
- **Clock-skew and replay window.** TOTP validation requires a bounded time-step tolerance, which is itself a narrow replay window. Standard practice (single-step tolerance, reject exact reuse of a consumed code) closes this to the extent RFC 6238 implementations generally do; it is not a residual this ADR treats as open, because no stronger property was asked for.
- **Should a native mobile client or an external-facing portal enter scope** (both out of scope per SRS §6.4 and ADR-0004's non-consequence), the phishing-resistance trade-off should be revisited rather than worked around, on the same precedent ADR-0004 sets for its own non-consequence.

## Related

- `docs/01-srs.md` HRMS-NFR-024 — the requirement this ADR implements a mechanism for.
- `docs/05-database-schema.md` §4.2 `second_factor`, `second_factor_recovery_request` — the schema this decision concretises.
- `docs/06-api-contracts.md` — named the trade-off and deferred it here.
- ADR-0004 — session cookie authentication; establishes the single-origin, no-third-party-consumer context this decision's rationale relies on.
- `docs/07-iam-rbac.md` §7.3, §8 — the recovery-approval path this decision assumes remains the sole fallback for a lost factor.
