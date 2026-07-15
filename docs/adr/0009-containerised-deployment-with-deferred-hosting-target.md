# ADR-0009: Containerised deployment with a deferred hosting target

**Status:** Accepted
**Date:** 2026-07-15
**Bears on:** TBD-003 (Hosting environment) — deliberately left open

## Context

Two constraints meet here.

**Technical.** ADR-0004 selects session cookie authentication, which requires the SPA and the API to share an origin. Cross-origin cookie delivery depends on `SameSite=None; Secure` and is increasingly restricted by browser third-party cookie policy. Deployment topology must therefore place both behind one origin.

**Legal, and unresolved.** The system holds personal data of Ghanaian employees. Ghana's Data Protection Act 2012 (Act 843) restricts transfer of personal data outside Ghana unless the destination provides an adequate level of protection. Ghana has published no adequacy list, so transfers require case-by-case assessment or reliance on a statutory exemption. Enforcement commenced in January 2026, with penalties reported up to GHS 3 million or 5% of annual turnover, whichever is higher. Section 27(1) requires data controllers to register with the Data Protection Commission. The Data Protection Bill 2025 proposes a more restrictive position, including a data localisation preference, transfer impact assessments, and Commission approval for high-risk transfers. Sources differ on how strictly the current Act is enforced in practice.

This is a legal question, not an engineering one. SRS §6.3 already provides the correct disposition: legal and regulatory requirements shall be confirmed with qualified HR, legal, payroll, and finance professionals before go-live.

Critically, the question **cannot** be answered now. TBD-001 records that the organisation is itself undetermined. There is no controller to register, no counsel to advise, and no production personal data. Selecting a hosting provider today would be precision without basis.

SRS §2.4 anticipates this: the server environment may be cloud-based or on-premises depending on organisational decision.

## Decision

Deployment is **containerised**: Docker with Docker Compose, comprising the Django application, Celery worker and scheduler, Redis, PostgreSQL, MinIO, and **Caddy** as reverse proxy.

Caddy serves the built React application at `/` and proxies `/api` to Django, presenting a **single origin** as ADR-0004 requires.

**The hosting target is deliberately deferred.** TBD-003 remains open.

## Decision rule for resolving TBD-003

The hosting target is selected when an operating organisation exists, and is subject to:

1. Written confirmation from qualified legal counsel on Act 843 obligations for personal data of Ghanaian employees, including the position of the Data Protection Bill 2025 if enacted by then.
2. Registration with the Data Protection Commission under section 27(1), where applicable to the controller.
3. Confirmation that the target satisfies HRMS-NFR-020 (HTTPS in production), HRMS-NFR-012 (backups), and HRMS-NFR-035 (95–98% availability during working hours).

Until all three are satisfied, no hosting commitment is made and none is implied by any development or demonstration deployment.

## Consequences

**Positive**

- The composition runs identically on a local machine, an on-premises server, an in-country provider, or a cloud platform. Resolving TBD-003 changes deployment configuration, not application code.
- SRS §2.4 is satisfied literally: the environment is genuinely an organisational decision, not one pre-empted by the architecture.
- The single-origin requirement from ADR-0004 is met by the reverse proxy in every environment, including local development, so the authentication path is exercised as deployed.
- The load described in HRMS-NFR-006 is well within a single modest host. No cloud-scale infrastructure is required, and none is adopted for appearance.

**Negative**

- Container orchestration, backup, monitoring, and TLS renewal are operational responsibilities of the deployment rather than a platform's.
- Deferral is not free: some operational characteristics, notably backup topology and availability measures against HRMS-NFR-035, cannot be finalised until the target is known.

**Rejected alternative**

- *Platform-as-a-service.* Faster to stand up, but binds the deployment to a provider, complicates the single-origin requirement, and locates personal data outside Ghana — pre-empting precisely the question this decision keeps open.

## Standing caveat

Nothing in this record constitutes legal advice. The obligations summarised above are drawn from secondary sources and are recorded to inform the decision rule, not to satisfy it. Qualified counsel determines the position.
