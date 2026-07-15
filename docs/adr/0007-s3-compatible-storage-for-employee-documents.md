# ADR-0007: S3-compatible object storage for employee documents

**Status:** Accepted
**Date:** 2026-07-15

## Context

HRMS-FR-006 requires authorised users to upload employee documents. HRMS-NFR-007 permits PDF, JPG, PNG, and DOCX. HRMS-NFR-008 caps document size at 5–10MB, configurable. HRMS-NFR-021 requires uploaded documents to be stored securely.

The documents are among the most sensitive artefacts the system holds: identity documents, contracts, certificates, and generated payslips.

Two constraints shape the choice:

- Both the web process and the Celery worker (ADR-0006) require access to stored files. The worker generates payslips and attaches documents to notifications.
- Where the data physically resides is an unresolved legal question, recorded in ADR-0009. Storage must not pre-empt it.

## Decision

Document storage uses an **S3-compatible object store**, accessed through `django-storages`. **MinIO** runs as a container in local and self-hosted deployments.

The bucket is **private**. Documents are never served from a directly addressable object URL. Every document request is authorised by the application first, against the visibility rules in ADR-0005, after which a **short-lived signed URL** is issued or the content is streamed through the application.

## Consequences

**Positive**

- **Deployment portability.** The S3 API is the portable interface. Moving between MinIO, a managed service, or an in-country provider is a configuration change, not a code change. This preserves the deferral in ADR-0009 rather than pre-answering it.
- **Data residency stays open.** MinIO is self-hostable, so documents can remain in-country or on-premises if required. A managed-only service would pin document data to a jurisdiction before the legal position is established.
- **Shared access.** Web and worker processes address the same bucket. A local filesystem volume would require a shared mount between containers and would not survive multi-host deployment.

**Negative**

- MinIO is an additional component to run and back up.
- Signed URL lifetime is a security parameter requiring deliberate choice: long enough to be usable, short enough that a leaked URL expires quickly.

## Security requirements

These are requirements, not recommendations.

- **The bucket is never public.** A public object URL is unauthenticated indefinitely and may be indexed. Serving a payslip or identity document from a public URL would breach HRMS-NFR-017, HRMS-NFR-019, and HRMS-NFR-021.
- **Authorisation precedes access.** Document requests are checked against the same visibility rules as record access. Storage is not a separate access-control domain.
- **File type is validated by content inspection**, not by file extension. An extension is client-supplied and is not evidence of file type (HRMS-NFR-007).
- **Size is enforced server-side** (HRMS-NFR-008). Client-side limits are a usability affordance, not a control.
- **Client-supplied filenames are not used as storage paths.** Stored object keys are generated. Client filenames are retained as metadata only.
