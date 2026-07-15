# ADR-0003: PostgreSQL as the database

**Status:** Accepted
**Date:** 2026-07-15
**Resolves:** TBD-004 (Database technology)

## Context

SRS §6.1 identifies 25 data entities — Employee, Department, Job Title, Reporting Relationship, Compensation Record, Payroll Record, Payslip, Leave Request, Leave Balance, Audit Log, and others. The relationships between them are dense and referentially significant: an organisational reporting structure, payroll records bound to active employees, leave balances bound to leave types.

The data carries specific obligations:

- Monetary values requiring exact arithmetic (HRMS-FR-036 to HRMS-FR-042).
- Payroll finalisation, which writes across payslip, deduction, and history records and must not be observable in a partial state (HRMS-BR-008).
- Uniqueness and validity constraints (HRMS-BR-001, HRMS-DR-001 to HRMS-DR-010).
- Configurable statutory rates, since rates change (SRS §2.5).
- Aggregate reporting across headcount, turnover, and payroll cost (HRMS-FR-049 to HRMS-FR-052).

## Decision

**PostgreSQL** is the database for all HRMS data.

## Consequences

**Positive**

- The `NUMERIC` type provides exact decimal arithmetic, paired with Python's `Decimal` in the application layer. Monetary values remain exact from calculation through storage.
- ACID transactions make payroll finalisation atomic. A failure mid-finalisation leaves no partially written payroll.
- Check and unique constraints enforce data rules at the storage layer, where application defects cannot bypass them. HRMS-DR-001, HRMS-DR-002, HRMS-DR-005, and HRMS-DR-006 are expressible as constraints rather than relying solely on application validation.
- Window functions and common table expressions support the Phase 3 reporting requirements without application-side aggregation.
- `JSONB` accommodates versioned statutory rate tables, satisfying the configurability constraint while keeping the relational core normalised.
- PostgreSQL is the best-supported backend for the Django ORM.

**Negative**

- Operational responsibility for backups, migrations, and version upgrades sits with the deployment (HRMS-NFR-012).
- Schema changes require migration discipline once production data exists.

**Rejected alternatives**

- *MySQL / MariaDB.* Viable, with domain precedent in OrangeHRM's LAMP deployment. Weaker constraint expression, JSON support, and analytic function coverage. No advantage identified for this system.
- *Document database.* Rejected. The domain is relational, and payroll finalisation requires multi-record atomicity that a document store does not guarantee across documents.
