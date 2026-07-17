# Technology Stack

**Human Resource Management System**

| | |
|---|---|
| Version | 1.1 |
| Prepared by | John Kessie |
| Organization | TBD |
| Date | July 2026 |
| Status | Approved |

## Revision History

| Name | Date | Reason for Changes | Version |
|---|---|---|---|
| John Kessie | July 2026 | Initial technology stack selection for HRMS | 1.0 |
| John Kessie | July 2026 | Add §4.3 Mail Dispatch: SMTP backend, provider deferred per TBD-001, ADR-0011 | 1.1 |

---

## 1. Introduction

### 1.1 Purpose

This document records the technology selection for the Human Resource Management System and the reasoning behind each choice. It resolves TBD-002 (final technology stack) and TBD-004 (database technology) from the Software Requirements Specification, and establishes the decision rule under which TBD-003 (hosting environment) will later be resolved.

This document does not describe system architecture, database schema, or API design. Those are addressed in the System Architecture Document, the Database Design, and the API Specification respectively.

### 1.2 Intended Audience

Software developers, system administrators, quality assurance testers, and technical stakeholders. Section 2 and Section 8 are relevant to project management and business stakeholders.

### 1.3 Basis of Selection

Selection was driven by the requirements set out in the Software Requirements Specification, in the following order of precedence:

1. Correctness obligations, particularly exact monetary arithmetic and payroll atomicity.
2. Security obligations, particularly role-based access control and protection of personal data.
3. Fitness for the functional shape of the system, which is dominated by record maintenance, workflow, and reporting.
4. Long-term maintainability by developers other than the original author.
5. Conformance to established practice.

Convenience of initial construction was not a selection criterion.

### 1.4 Related Documents

| Document | Content |
|---|---|
| `docs/01-srs.md` | Software Requirements Specification v1.0. Authoritative |
| `CONTEXT.md` | Domain glossary and design constraints |
| `docs/adr/` | Architecture decision records |

---

## 2. Summary

| Layer | Selection |
|---|---|
| Architecture | Modular monolith backend, separate single-page application client |
| Backend language | Python |
| Backend framework | Django with Django REST Framework |
| Database | PostgreSQL |
| Background processing | Celery with Celery Beat |
| Message broker and cache | Redis (two instances: broker, cache) |
| Object storage | S3-compatible; MinIO for self-hosted deployment |
| Frontend build | Vite |
| Frontend language | TypeScript |
| Frontend framework | React |
| UI component library | Ant Design |
| Server state management | TanStack Query |
| Client routing | React Router |
| Authentication | Django server-side sessions, cookie-borne |
| Containerisation | Docker with Docker Compose |
| Reverse proxy | Caddy |
| Hosting target | Deferred; see Section 7 |

---

## 3. Architecture

The backend is a modular monolith: a single deployable divided internally into modules with explicit boundaries, one per functional area. The frontend is a separate React single-page application consuming a REST API. Both are served under a single origin.

Independently deployable services were rejected as disproportionate to a system serving 50 to 200 concurrent users (HRMS-NFR-006), and contrary to prevailing guidance that favours a modular monolith until a specific operational need justifies extraction.

Domain logic within each module is held in framework-light service code, separated from HTTP handling and persistence. This permits a module's logic to be extracted for use in another system without carrying framework dependencies.

Recorded in ADR-0001.

## 4. Backend

### 4.1 Django and Django REST Framework

The system's demands are weighted toward domain logic rather than request throughput: configurable statutory payroll calculation, background batch processing, role-based access control across seven user classes, an administrative surface for HR operations, and audit logging.

Django provides authentication, groups and permissions, an administrative interface, and a migration system. Its application concept maps directly onto the module boundaries described in Section 3. Django REST Framework provides the API layer and schema generation for the API Specification deliverable.

Python's `Decimal` type provides exact arithmetic for statutory deduction calculation. Binary floating point is not used for monetary values.

Node-based full-stack frameworks were rejected: they provide no native background processing, scheduling, or administrative capability, each of which this system requires. Laravel was evaluated as a legitimate alternative with strong precedent in this domain and was not selected.

Recorded in ADR-0002.

### 4.2 Background Processing

Celery provides task execution, Celery Beat provides scheduling, and Redis serves as message broker. The broker runs as its own Redis instance, configured `noeviction` with AOF persistence and kept separate from the cache instance, so that cache eviction cannot discard a queued payroll task. Recorded in ADR-0006.

Background processing is required rather than optional. Payroll processing is expected to complete within a few minutes (HRMS-NFR-005), which exceeds a reasonable request lifetime. Leave accrual is calendar-driven. Payslip generation, bank transfer file generation, notification delivery, and large report exports are batch operations.

Payroll tasks must be idempotent. A retried task must not produce duplicate payroll records. Given HRMS-BR-008 and the monetary consequences of error, task semantics are a first-order concern of the Payroll module design.

Recorded in ADR-0006.

### 4.3 Mail Dispatch

Email is sent through Django's SMTP email backend, configured entirely from the environment (host, port, credentials, TLS, sender address) rather than against a named provider. No transactional email provider (e.g. SES, SendGrid) is selected at this time.

This mirrors the deferral already made for hosting (Section 7.2) and document storage (Section 5.2): TBD-001 leaves the deploying organisation undetermined, and a provider choice made now would have no basis. The SMTP backend is a portable interface in the same sense the S3 API is for storage — pointing `EMAIL_HOST` at a different provider is a configuration change, not a code change. Local development and end-to-end verification use Mailpit, a disposable SMTP catcher, so mail can be confirmed as sent without a real provider or a real mailbox.

Mail dispatch runs as a Celery task off the request cycle, with bounded retry and delivery-failure logging to the application log rather than `audit_log`. Recorded in ADR-0011.

## 5. Data

### 5.1 PostgreSQL

PostgreSQL is the database for all HRMS data.

The `NUMERIC` type provides exact decimal arithmetic, paired with `Decimal` in application code, so monetary values remain exact from calculation through storage. Transactions make payroll finalisation atomic, as HRMS-BR-008 requires. Check and unique constraints enforce HRMS-DR-001, HRMS-DR-002, HRMS-DR-005, and HRMS-DR-006 at the storage layer, where application defects cannot bypass them. Window functions support the Phase 3 reporting requirements. `JSONB` accommodates versioned statutory rate tables, satisfying the configurability constraint of SRS §2.5 while keeping the relational core normalised.

MySQL and MariaDB were considered and offer no advantage for this system. Document databases were rejected: the domain is relational, and payroll finalisation requires multi-record atomicity.

Resolves TBD-004. Recorded in ADR-0003.

### 5.2 Document Storage

Employee documents are held in S3-compatible object storage, accessed through `django-storages`. MinIO runs as a container in self-hosted deployment.

The S3 API is a portable interface: relocating storage between MinIO, a managed service, or an in-country provider is a configuration change rather than a code change. This preserves the deferral described in Section 7. MinIO being self-hostable, documents may remain in-country or on-premises where required.

The bucket is private. Documents are never served from a directly addressable object URL. Each request is authorised by the application before a short-lived signed URL is issued. File type is validated by content inspection rather than by extension, size is enforced server-side, and stored object keys are generated rather than taken from client-supplied filenames.

Recorded in ADR-0007.

## 6. Frontend

### 6.1 Composition

| Concern | Selection |
|---|---|
| Build tooling | Vite |
| Language | TypeScript |
| Framework | React |
| Components | Ant Design |
| Forms | Ant Design Form |
| Server state | TanStack Query |
| Routing | React Router |
| Boundary validation | Zod |

TypeScript is used throughout. The system carries 71 functional requirements, access control on every surface, and monetary values; static typing constrains drift between the API and the client.

Zod is applied at the API boundary to validate response shape, so that backend contract drift surfaces as an explicit error rather than as an undefined value in the interface. It is not used for form field validation, which Ant Design's Form component provides.

### 6.2 Ant Design

The interface is dominated by forms, data tables, approval queues, and role-specific dashboards. SRS §3.1 requires consistent buttons, tables, forms, menus, and status labels; HRMS-NFR-025 to HRMS-NFR-027 require a clean, professional interface usable by non-technical staff.

Ant Design is built for enterprise administrative interfaces, which is the shape of this system. Table sorting, filtering, pagination, and export are provided rather than assembled. The agreed visual target — flat, border-defined cards with small corner radius, a single accent colour, and dense tables — is achievable through Ant Design's design token system.

Material UI was rejected on a specific ground: capable data grid features sit behind a paid licence tier, a boundary this table-heavy system would reach early. A component-ownership approach using shadcn/ui with Tailwind and TanStack Table was rejected because the agreed visual target does not require it and the assembly cost across the module set is not repaid.

Recorded in ADR-0008.

## 7. Deployment

### 7.1 Containerisation

The system is deployed as containers orchestrated by Docker Compose: the Django application, Celery worker and scheduler, two Redis instances (broker and cache), PostgreSQL, MinIO, and Caddy as reverse proxy.

Caddy serves the built React application at `/` and proxies `/api` to Django, presenting a single origin. This satisfies the requirement of the authentication design described in Section 8 in every environment, including local development, so that the authentication path is exercised as deployed.

The composition runs identically on a local machine, an on-premises server, an in-country provider, or a cloud platform.

### 7.2 Hosting Target

**The hosting target is deferred. TBD-003 remains open.**

This is a decision, not an omission. SRS §2.4 states that the server environment may be cloud-based or on-premises depending on organisational decision. TBD-001 records that the organisation itself is undetermined; there is no controller, no counsel, and no production personal data. A hosting selection made now would have no basis.

The system holds personal data of Ghanaian employees. Ghana's Data Protection Act 2012 (Act 843) requires a controller to register with the Data Protection Commission and to disclose the countries it transfers personal data to. Whether it further restricts where such data may reside is an **open question of legal interpretation**, not a settled constraint this document may state as one — the Act sets out no adequacy regime of the kind the GDPR establishes. SRS §6.3 provides the correct disposition: legal and regulatory requirements shall be confirmed with qualified professionals before go-live. Nothing in this document constitutes legal advice.

The hosting target is selected when an operating organisation exists, subject to:

1. Written confirmation from qualified legal counsel on obligations under Act 843 for personal data of Ghanaian employees, including whether the Act restricts transfer of that data outside Ghana and on what test.
2. Registration with the Data Protection Commission where applicable to the controller.
3. Confirmation that the target satisfies HRMS-NFR-020 (HTTPS in production), HRMS-NFR-012 (backups), and HRMS-NFR-035 (95–98% availability during working hours).

Until all three are satisfied, no hosting commitment is made, and none is implied by any development or demonstration deployment.

Recorded in ADR-0009.

## 8. Authentication and Access Control

### 8.1 Authentication

Authentication uses Django server-side sessions carried by a cookie set `HttpOnly`, `Secure`, and `SameSite=Lax`. Bearer tokens are not used.

Three requirements determine this. HRMS-BR-012 requires that terminated, resigned, and retired employees lose portal access; deleting a server-side session revokes access immediately, whereas a bearer token remains valid until expiry irrespective of account state. HRMS-NFR-023 requires inactivity expiry, which is a server-side session property. HRMS-NFR-022 requires audit logging of authentication events, for which server-side session state provides a single natural location.

A cookie set `HttpOnly` is not readable by client script. Given that the system holds salary figures, SSNIT and PAYE records, and identity documents, this is the stronger posture.

Because credentials are attached automatically by the browser, CSRF verification is required on state-changing endpoints and is not to be disabled.

The advantages of bearer tokens — stateless verification across independent services, and credentials shared across multiple client types — do not apply. The backend is a single monolith, there are no third-party API consumers, and a native mobile application is out of scope per SRS §6.4. Should a native client enter scope, this decision is to be revisited rather than worked around.

This design requires a single origin, which Section 7.1 provides.

Recorded in ADR-0004.

### 8.2 Access Control

Access control operates at two levels.

**Action-level** access uses Django groups and permissions. Each **assigned** role maps to a group, governing which operations a user may perform. The two **derived** roles, Employee and Manager, attach from employment and reporting data rather than from a grant, and have no group. Recorded in ADR-0010.

**Row-level** access uses queryset scoping: a visibility rule per module, expressed as a manager method deriving visibility from organisational data. This satisfies HRMS-NFR-017, HRMS-NFR-018, HRMS-NFR-019, HRMS-BR-006, and HRMS-BR-007.

Object-level permission records were rejected. HRMS-FR-008 requires the system to hold reporting relationships, so a manager's team is already a fact in the data. Permission records would duplicate that fact and drift from it: when an employee's reporting manager changes, stale records would leave the former manager with continued visibility of that employee's data. Derived scoping cannot drift, because it reads the organisational structure at query time.

The cost of this approach is that nothing enforces its application. An endpoint omitting the scoped queryset returns unscoped data. Accordingly: every endpoint returning employee-scoped data obtains its queryset through a visibility rule; permission tests accompany every module, asserting both permitted and denied paths; and review treats a missing scope call as a blocking defect.

Recorded in ADR-0005.

## 9. Quality Assurance Tooling

| Concern | Selection |
|---|---|
| Backend testing | pytest with pytest-django |
| Test data | factory_boy |
| Frontend unit testing | Vitest with React Testing Library |
| End-to-end and browser testing | Playwright |
| API schema generation | drf-spectacular |

The project testing strategy requires functional, validation, permission, integration, browser, and end-to-end testing for every module. Permission testing is of particular consequence given Section 8.2.

drf-spectacular generates the OpenAPI schema from the API implementation, which supplies the API Specification deliverable and keeps it consistent with the served API.

## 10. Requirements Traceability

| Requirement | Addressed by |
|---|---|
| HRMS-NFR-006 (50–200 concurrent users) | §3, §7.1 |
| HRMS-NFR-005 (payroll within minutes) | §4.2 |
| HRMS-NFR-012 (backups) | §7.2 — pending hosting resolution |
| HRMS-NFR-013, HRMS-NFR-022 (audit logging) | §4.1, §8.1 |
| HRMS-NFR-014, HRMS-NFR-015 (authentication) | §8.1 |
| HRMS-NFR-016 (role-based access control) | §8.2 |
| HRMS-NFR-017, HRMS-NFR-018, HRMS-NFR-019 (data visibility) | §8.2 |
| HRMS-NFR-020 (HTTPS in production) | §7.2 — pending hosting resolution |
| HRMS-NFR-021 (secure document storage) | §5.2 |
| HRMS-NFR-023 (session expiry) | §8.1 |
| HRMS-NFR-007, HRMS-NFR-008 (file type and size) | §5.2 |
| HRMS-NFR-025 to HRMS-NFR-027 (usability) | §6.2 |
| HRMS-NFR-030 to HRMS-NFR-032 (maintainability) | §3 |
| HRMS-NFR-035 (availability) | §7.2 — pending hosting resolution |
| HRMS-BR-008 (payroll approval, atomicity) | §5.1 |
| HRMS-BR-012 (access on termination) | §8.1 |
| HRMS-DR-001 to HRMS-DR-010 (validation) | §5.1 |

## 11. Outstanding Items

| Item | Status |
|---|---|
| TBD-002 — final technology stack | **Resolved** by this document |
| TBD-004 — database technology | **Resolved** by this document (§5.1) |
| TBD-003 — hosting environment | **Open by decision.** Decision rule in §7.2 |
| TBD-011 — mobile application in first release | **Resolved** by SRS §2.5 and §6.4: web-first, native application out of scope |
| TBD-010 — exact user roles and permissions | **Resolved** by `docs/07-iam-rbac.md`. Eight roles serve the seven SRS §2.3 user classes; role model, derivation rules, permission matrix, and visibility rules are settled |
| TBD-005 — final payroll statutory rates | **Open.** Rates are configuration, not code (§5.1). Requires qualified payroll or finance confirmation |
| TBD-006 — bank transfer file format | **Open.** Depends on the organisation's bank |
| TBD-009 — document retention policy | **Open.** Bears on §5.2 |
| TBD-015 — data migration approach | **Open** |
