# Software Requirements Specification

**Human Resource Management System**

| | |
|---|---|
| Version | 1.3 |
| Prepared by | John Kessie |
| Organization | TBD |
| Date Created | May 2026 |

## Revision History

| Name | Date | Reason for Changes | Version |
|---|---|---|---|
| John Kessie | May 2026 | Initial SRS document for HRMS | 1.0 |
| John Kessie | 2026-07-15 | HRMS-NFR-024 promoted from a recommendation to a *shall*: multi-factor authentication is mandatory for administrators and payroll users, and the second factor is placed outside the control of the roles that administer accounts and credentials, including at enrollment and recovery. This closes the gap against HRMS-NFR-019, a *shall*, which was unenforceable while a System Administrator could reset a payroll user's credentials under §2.3.1 and authenticate as them. HRMS-FR-051 deferred to later versions on the pattern of HRMS-FR-055, the training data its condition presupposed being excluded by §6.4; §2.2 and §4.5 reconciled. Equity mentions removed from §2.2 and §4.6, no functional requirement having covered them. HRMS-NFR-001 to HRMS-NFR-006 restated as measurable thresholds at the upper bound of each stated range, at the 95th percentile, over a stated measurement window, at a workload pinned to 200 concurrent users; the data volumes they are verified against are recorded as TBD-016 and HRMS-NFR-005's threshold as TBD-017, neither being stated in this document. §2.2 predictive attrition analytics marked deferred, aligning the summary with HRMS-FR-055. No requirement other than HRMS-NFR-024 changes modality, and no scope is added or removed | 1.1 |
| John Kessie | 2026-07-18 | **HRMS-FR-028/HRMS-FR-044 and HRMS-FR-029/HRMS-FR-063 are duplicate pairs, found while scoping Module 11 (Employee Self-Service) against `docs/02-project-plan.md` §6.1's build order.** §4.3 (self-service) and §4.4 (Payroll) both state "the system shall allow employees to view their own payslips", verbatim, as FR-028 and FR-044; §4.3 and §4.7 (Leave Management) both state the same leave-submission requirement as FR-029 and FR-063. Each pair had been assigned to two different modules by the plan, which read as Employee Self-Service (module 11) depending on unbuilt Payroll (16) and Leave Management (13) — a sixth instance of the provider-precedes-consumer defect this project's plan has caught five times before, except here the defect is duplication, not a genuine second requirement scheduled early. FR-044 and FR-063 are marked canonical; FR-028 and FR-029 are marked as restating them, not superseding or removing them, since neither this project's convention nor traceability tooling assumes requirement IDs are renumbered once assigned. No requirement's modality, scope, or module ownership beyond this correction changes. Filed as DOC-009; `docs/02-project-plan.md` and `docs/04-system-architecture.md` reconciled in the same change | 1.2 |
| John Kessie | 2026-07-18 | **HRMS-FR-031 duplicates HRMS-FR-064, found while scoping Module 12 (Manager Self-Service) — the same pattern DOC-009 found in Module 11, checked for on the strength of that precedent rather than stumbled on independently.** §4.3's "Manager Approves Request" stimulus/response sequence and FR-031 ("approve or reject requests") name no request type; §4.7's FR-064 is the same action, qualified to "leave requests" — and no other manager-approval workflow exists anywhere in this document for FR-031 to mean. FR-064 is marked canonical; FR-031 is marked as restating it. **Unlike FR-028/FR-029, HRMS-FR-032 (manager team-level reports) is not part of this correction** — `docs/06-api-contracts.md` §4.15 assigns it to Reports (module 17) as a genuine, distinct read surface, not a restatement of any other requirement; it is a real forward dependency, recorded as a deferred residual at `docs/02-project-plan.md` rather than resolved here. Filed as DOC-010; `docs/02-project-plan.md` reconciled in the same change | 1.3 |
| John Kessie | 2026-07-26 | §3.4 amended: SMS added as an opt-in notification channel (pending-task and request-update categories), subject to user preference and a verified phone number on the account. No existing notification-triggering event's delivery changes as part of this revision — the mechanism is added, not switched on for any event. See docs/superpowers/specs/2026-07-26-notifications-email-sms-design.md. | 1.4 |

---

## Table of Contents

- Revision History
- 1. Introduction
  - 1.1 Purpose
  - 1.2 Document Conventions
  - 1.3 Intended Audience and Reading Suggestions
  - 1.4 Product Scope
  - 1.5 References
- 2. Overall Description
  - 2.1 Product Perspective
  - 2.2 Product Functions
  - 2.3 User Classes and Characteristics
  - 2.4 Operating Environment
  - 2.5 Design and Implementation Constraints
  - 2.6 User Documentation
  - 2.7 Assumptions and Dependencies
- 3. External Interface Requirements
  - 3.1 User Interfaces
  - 3.2 Hardware Interfaces
  - 3.3 Software Interfaces
  - 3.4 Communications Interfaces
- 4. System Features
  - 4.1 Core HR
  - 4.2 Recruitment and Onboarding
  - 4.3 Employee Self-Service and Manager Self-Service
  - 4.4 Payroll
  - 4.5 Reporting and Analytics
  - 4.6 Compensation and Benefits
  - 4.7 Leave Management
- 5. Other Nonfunctional Requirements
  - 5.1 Performance Requirements
  - 5.2 Safety Requirements
  - 5.3 Security Requirements
  - 5.4 Software Quality Attributes
  - 5.5 Business Rules
- 6. Other Requirements
- Appendix A: Glossary
- Appendix B: Analysis Models
- Appendix C: To Be Determined List

---

## 1. Introduction

### 1.1 Purpose

This Software Requirements Specification defines the functional and nonfunctional requirements for the Human Resource Management System.

The purpose of this document is to guide stakeholders, developers, testers, project managers, HR officers, payroll officers, and system administrators in understanding what the system must do, how it should behave, and the boundaries of the project.

This SRS covers the phased development of the HRMS across three major phases:

- Phase 1: Core HR; Recruitment and Onboarding
- Phase 2: Employee Self-Service and Manager Self-Service; Payroll
- Phase 3: Reporting and Analytics; Compensation and Benefits; Leave Management

This document does not describe final UI design details, database schema implementation, or source code architecture. Those should be handled in separate technical design documents.

### 1.2 Document Conventions

- "Shall" indicates a mandatory system requirement.
- "Should" indicates a recommended requirement.
- "May" indicates an optional requirement.
- Requirements are uniquely identified using labels such as HRMS-FR-001.
- Priorities are classified as High, Medium, or Low.
- TBD means the item is yet to be determined and must be clarified before implementation.

### 1.3 Intended Audience and Reading Suggestions

This document is intended for project managers, software developers, UI/UX designers, quality assurance testers, HR administrators, payroll officers, business analysts, system administrators, and management stakeholders.

- Business stakeholders should focus on Sections 1, 2, 4, and 5.
- Developers should focus on Sections 3, 4, 5, and 6.
- Testers should focus on Sections 4 and 5.
- System administrators should focus on Sections 2.4, 3, 5.3, and 6.
- HR and payroll users should focus on Sections 2.2, 2.3, 4, and 5.5.

### 1.4 Product Scope

The Human Resource Management System is a software platform designed to help organizations manage employee information, recruitment, onboarding, payroll, self-service requests, leave, compensation, benefits, and HR reporting.

The system will replace or reduce manual HR processes such as spreadsheets, paper files, email-based approvals, and disconnected payroll records.

- Centralize employee records.
- Improve HR data accuracy.
- Support recruitment and onboarding workflows.
- Enable employee and manager self-service.
- Support payroll processing for Ghana-based statutory deductions.
- Track leave balances and approvals.
- Provide HR reports and analytics.
- Improve security and accountability through role-based access and audit logs.

### 1.5 References

| Reference | Description |
|---|---|
| Ghana PAYE Requirements | Payroll tax requirement to be confirmed with current Ghana Revenue Authority rules. |
| SSNIT Tier 1, Tier 2, and Tier 3 Pension Rules | Statutory and voluntary pension contribution requirements for Ghana. |
| Organization HR Policy Document | TBD |
| Organization Payroll Policy Document | TBD |
| Organization Leave Policy Document | TBD |
| Organization Data Protection Policy | TBD |

---

## 2. Overall Description

### 2.1 Product Perspective

The HRMS is a new web-based software system intended to serve as a centralized HR platform for an organization.

The system will support HR operations from employee record management to recruitment, onboarding, payroll, leave management, reporting, compensation, and benefits.

The HRMS may later integrate with external systems such as email services, job boards, bank payment systems, accounting systems, biometric attendance systems, and government tax or pension platforms. These integrations are not all required for the first release.

The system will be developed in phases to reduce implementation risk and allow the organization to validate each major HR function before expanding to more advanced features.

### 2.2 Product Functions

#### Phase 1

**Core HR**

- Manage employee master records.
- Store personal details.
- Store job information.
- Store employment history.
- Store compensation details.
- Store employee documents.
- Store emergency contacts.
- Define reporting relationships.

**Recruitment and Onboarding**

- Manage job requisitions.
- Post jobs internally or externally.
- Track applicants.
- Schedule interviews.
- Generate offer letters.
- Convert successful candidates into employee records.
- Track onboarding tasks.

#### Phase 2

**Employee Self-Service and Manager Self-Service**

- Allow employees to update selected personal details.
- Allow employees to view payslips.
- Allow employees to request leave.
- Allow managers to approve requests.
- Allow managers to view team data.
- Allow managers to run reports.

**Payroll**

- Calculate salaries.
- Calculate allowances.
- Calculate statutory deductions.
- Support PAYE.
- Support SSNIT Tier 1.
- Support Tier 2 pension.
- Support Tier 3 voluntary contributions.
- Generate payslips.
- Generate bank transfer files.

#### Phase 3

**Reporting and Analytics**

- Provide headcount dashboards.
- Provide turnover reports.
- Provide payroll cost reports.
- Support predictive analytics on attrition risk in later versions where enough historical data exists (deferred; see HRMS-FR-055).

**Compensation and Benefits**

- Manage salary structures.
- Manage pay grades.
- Manage bonus cycles.
- Manage benefits enrollment.

**Leave Management**

- Allow employees to request leave.
- Route approvals through managers.
- Track leave balances by leave type.
- Enforce leave policy rules.

### 2.3 User Classes and Characteristics

#### 2.3.1 System Administrator

The System Administrator manages system configuration, user accounts, roles, permissions, and audit access.

- High system privilege.
- Technical or semi-technical user.
- Uses the system occasionally for configuration and maintenance.
- Requires access to user management and audit functions.

#### 2.3.2 HR Administrator / HR Officer

The HR Administrator manages employee records and HR workflows.

- Frequent system user.
- Requires access to employee records, recruitment, onboarding, leave, and reports.
- Requires strong data entry and review permissions.
- Should not automatically access technical system configuration unless assigned.

#### 2.3.3 Recruiter

The Recruiter manages hiring activities.

- Uses recruitment and onboarding modules.
- Tracks candidates and interview stages.
- May not need access to payroll or compensation records.
- Requires candidate communication and offer letter features.

#### 2.3.4 Employee

The Employee uses the self-service portal.

- Regular user.
- Limited access.
- Can view and update selected personal information.
- Can view own payslips.
- Can submit leave requests.
- Cannot access other employee records.

#### 2.3.5 Manager / Supervisor

The Manager approves requests and views team information.

- Moderate system privilege.
- Can view assigned team members.
- Can approve or reject requests.
- Can access team reports.
- Cannot access company-wide sensitive HR or payroll data unless authorized.

#### 2.3.6 Payroll Officer

The Payroll Officer manages payroll operations.

- High access to payroll data.
- Requires access to salary, deductions, allowances, payslips, and payroll history.
- Should have restricted access separated from general HR roles.
- Requires approval workflow support for payroll finalization.

#### 2.3.7 Executive / Management User

The Executive user views dashboards and high-level reports.

- Uses the system mainly for decision-making.
- Requires summarized reports, not full operational access.
- Should have read-only access to approved dashboards and analytics.

### 2.4 Operating Environment

- Web-based application accessible through modern browsers.
- Supported browsers: Google Chrome, Microsoft Edge, Mozilla Firefox, and Safari.
- Responsive interface for desktop, tablet, and mobile browsers.
- Server environment may be cloud-based or on-premise depending on organizational decision.
- Database server shall store employee, recruitment, payroll, leave, compensation, and audit data.
- Production environment shall use HTTPS.
- The system should support future mobile app integration.

### 2.5 Design and Implementation Constraints

- The system must follow role-based access control.
- Sensitive HR and payroll data must be protected.
- Ghana payroll calculations must consider PAYE, SSNIT Tier 1, Tier 2, and Tier 3 contributions.
- Payroll rules must be configurable because statutory rates may change.
- The first version should focus on practical HR operations rather than complex enterprise automation.
- Predictive analytics depends on the quality of historical HR data.
- Bank transfer file formats may vary depending on the organization's bank.
- External job board posting may depend on third-party API availability.
- Web-first development is preferred before building a full native mobile application.
- User interface should be simple enough for non-technical HR staff and employees.

### 2.6 User Documentation

- System administrator guide
- HR administrator user guide
- Employee self-service guide
- Manager self-service guide
- Payroll processing guide
- Recruitment and onboarding guide
- Leave management guide
- Basic troubleshooting guide
- Frequently asked questions
- Short training videos or walkthroughs, if budget allows

### 2.7 Assumptions and Dependencies

The project assumes that:

- The organization has existing HR policies.
- The organization will provide employee data for migration or entry.
- HR will define departments, roles, job titles, pay grades, leave types, and approval workflows.
- Payroll rules will be validated by qualified payroll or finance personnel.
- Users will have valid email addresses or login credentials.
- Internet access will be available to users.
- Management will approve the phased implementation approach.
- HR staff will be trained before go-live.
- The organization will define who can access sensitive data.

The project depends on:

- Availability of HR policy documents.
- Availability of payroll rules.
- Availability of employee records.
- Availability of management approvals.
- Availability of technical hosting infrastructure.
- Availability of accurate statutory deduction rules.

---

## 3. External Interface Requirements

### 3.1 User Interfaces

The HRMS shall provide web-based user interfaces for login and password reset, dashboard, employee records, recruitment, onboarding, employee self-service, manager self-service, payroll, reporting and analytics, compensation and benefits, leave management, and system administration.

- Be clean, professional, and easy to navigate.
- Use clear form labels and validation messages.
- Provide role-specific dashboards.
- Provide search and filter functions where necessary.
- Support responsive layouts for desktop, tablet, and mobile screens.
- Display error messages clearly.
- Prevent users from accessing unauthorized pages.
- Use consistent buttons, tables, forms, menus, and status labels.

### 3.2 Hardware Interfaces

The HRMS is primarily a web-based system and does not require specialized hardware for the initial release.

- Desktop computers
- Laptops
- Tablets
- Smartphones

Optional future hardware integrations may include biometric attendance devices, ID card scanners, and document scanners. These hardware integrations are out of scope for the first version unless approved later.

### 3.3 Software Interfaces

| Software Component | Purpose |
|---|---|
| Database Management System | Store HRMS records |
| Email Service | Send notifications and password reset emails |
| Web Server / Application Server | Host the HRMS application |
| Authentication Service | Manage login, sessions, and access control |
| File Storage System | Store employee documents and generated files |
| Payroll Calculation Engine | Process salary, deductions, and allowances |
| Reporting Engine | Generate dashboards and reports |
| Bank File Export Format | Generate bank transfer files |
| Job Board APIs | Future job posting integration |

The exact technology stack is TBD and should be confirmed during technical architecture planning.

### 3.4 Communications Interfaces

- HTTPS for secure browser-server communication.
- Email notifications for approvals, onboarding, password reset, and payroll-related communication.
- In-app notifications for pending tasks and request updates.
- SMS notifications, opt-in, for pending-task and request-update categories, subject to user preference and a verified phone number.
- Secure file upload and download.
- API-based communication between frontend and backend, where applicable.
- Future third-party integrations using secure API protocols.

All production communication involving sensitive data shall be encrypted.

---

## 4. System Features

### 4.1 Core HR

#### 4.1 Description and Priority

Core HR is the foundation of the HRMS. It stores and manages the employee master record, personal details, job information, employment history, compensation, documents, emergency contacts, and reporting relationships.

Priority: High

#### 4.1 Stimulus/Response Sequences

- Create Employee Record: HR Officer logs in, opens Core HR, selects Create Employee, enters required details, submits the form, and the system validates and creates the employee record.
- Update Employee Record: HR Officer searches for an employee, selects a profile, updates allowed fields, and the system saves the updated record and records audit history.

#### 4.1 Functional Requirements

HRMS-FR-001: The system shall allow authorized HR users to create employee records.

HRMS-FR-002: The system shall store employee personal details.

HRMS-FR-003: The system shall store employee job information.

HRMS-FR-004: The system shall store employee employment history.

HRMS-FR-005: The system shall store employee compensation details.

HRMS-FR-006: The system shall allow authorized users to upload employee documents.

HRMS-FR-007: The system shall store emergency contact information.

HRMS-FR-008: The system shall support employee reporting relationships.

HRMS-FR-009: The system shall allow authorized users to search and filter employee records.

HRMS-FR-010: The system shall maintain audit history for sensitive employee record changes.

HRMS-FR-011: The system shall prevent duplicate employee IDs.

HRMS-FR-012: The system shall allow HR to update employee status.

### 4.2 Recruitment and Onboarding

#### 4.2 Description and Priority

Recruitment and Onboarding manages job requisitions, job postings, applicant tracking, interview scheduling, offer letters, and onboarding tasks.

Priority: High

#### 4.2 Stimulus/Response Sequences

- Create Job Requisition: Recruiter logs in, opens Recruitment, creates a job requisition, enters job details, submits it, and the system saves the requisition with the appropriate status.
- Move Candidate to Offer Stage: Recruiter opens a candidate profile, updates the status to Offer, generates an offer letter, and the system stores the offer letter record.

#### 4.2 Functional Requirements

HRMS-FR-013: The system shall allow authorized users to create job requisitions.

HRMS-FR-014: The system shall allow job requisitions to have approval statuses.

HRMS-FR-015: The system shall allow authorized users to create job postings.

HRMS-FR-016: The system shall store candidate profiles.

HRMS-FR-017: The system shall track candidate application stages.

HRMS-FR-018: The system shall allow interview scheduling.

HRMS-FR-019: The system shall store interview feedback.

HRMS-FR-020: The system shall allow offer letter generation.

HRMS-FR-021: The system shall track offer acceptance or rejection.

HRMS-FR-022: The system shall convert successful candidates into employee records.

HRMS-FR-023: The system shall support onboarding checklists.

HRMS-FR-024: The system shall track onboarding task completion.

### 4.3 Employee Self-Service and Manager Self-Service

#### 4.3 Description and Priority

Employee Self-Service and Manager Self-Service are portals where employees can update selected details, view payslips, request leave, and where managers can approve requests, view team data, and run reports. Priority: High

#### 4.3 Stimulus/Response Sequences

- Employee Updates Personal Details: Employee logs in, opens profile, updates allowed personal information, and the system validates and saves the update or routes it for HR approval.
- Manager Approves Request: Manager receives a notification, opens request details, approves or rejects the request, and the system updates the status and notifies the employee.

#### 4.3 Functional Requirements

HRMS-FR-025: The system shall allow employees to view their own profiles.

HRMS-FR-026: The system shall allow employees to update selected personal details.

HRMS-FR-027: The system shall restrict employees from editing salary, job title, department, employment status, and reporting manager.

HRMS-FR-028: The system shall allow employees to view their own payslips. *(Duplicate of HRMS-FR-044, §4.4. Payroll (module 16) is the canonical owner; this restates the same requirement in the self-service use case, not a second one — see revision history v1.2.)*

HRMS-FR-029: The system shall allow employees to submit leave requests. *(Duplicate of HRMS-FR-063, §4.7. Leave Management (module 13) is the canonical owner; this restates the same requirement in the self-service use case, not a second one — see revision history v1.2.)*

HRMS-FR-030: The system shall allow managers to view assigned team members.

HRMS-FR-031: The system shall allow managers to approve or reject requests. *(Duplicate of HRMS-FR-064, §4.7. Leave Management (module 13) is the canonical owner — no other manager-approval workflow exists in this SRS for this requirement to name; this restates the same requirement in the self-service use case, not a second one — see revision history v1.3.)*

HRMS-FR-032: The system shall allow managers to view team-level reports.

HRMS-FR-033: The system shall notify managers of pending approvals.

HRMS-FR-034: The system shall notify employees of approval decisions.

### 4.4 Payroll

#### 4.4 Description and Priority

Payroll calculates salaries, statutory deductions, allowances, payslips, and bank transfer files. For Ghana, payroll must consider PAYE, SSNIT Tier 1, Tier 2 pension, and Tier 3 voluntary contributions.

Priority: High

#### 4.4 Stimulus/Response Sequences

- Process Payroll: Payroll Officer selects payroll period, system loads active employees, calculates allowances and deductions, approver reviews and approves payroll, and the system finalizes payroll and generates payslips and bank transfer file.

#### 4.4 Functional Requirements

HRMS-FR-035: The system shall allow authorized users to configure salary components.

HRMS-FR-036: The system shall calculate basic salary.

HRMS-FR-037: The system shall calculate allowances.

HRMS-FR-038: The system shall calculate deductions.

HRMS-FR-039: The system shall support PAYE calculations.

HRMS-FR-040: The system shall support SSNIT Tier 1 deductions.

HRMS-FR-041: The system shall support Tier 2 pension deductions.

HRMS-FR-042: The system shall support Tier 3 voluntary contributions.

HRMS-FR-043: The system shall generate payslips.

HRMS-FR-044: The system shall allow employees to view their own payslips. *(Canonical; HRMS-FR-028, §4.3, restates this requirement and is not a second one.)*

HRMS-FR-045: The system shall generate payroll summary reports.

HRMS-FR-046: The system shall generate bank transfer files.

HRMS-FR-047: The system shall require approval before payroll finalization.

HRMS-FR-048: The system shall maintain payroll history.

### 4.5 Reporting and Analytics

#### 4.5 Description and Priority

Reporting and Analytics provides dashboards on headcount, turnover, and payroll costs. Training completion reporting (HRMS-FR-051) and predictive analytics on attrition risk (HRMS-FR-055) are deferred to later versions and are not delivered by this module in the first version.

Priority: Medium

#### 4.5 Stimulus/Response Sequences

- Generate Headcount Report: HR Officer opens Reporting, selects headcount report, applies filters, and the system displays or exports the report.

#### 4.5 Functional Requirements

HRMS-FR-049: The system shall provide headcount dashboards.

HRMS-FR-050: The system shall provide turnover reports.

HRMS-FR-051: The system shall support training completion reports in later versions where a source of training data exists.

HRMS-FR-052: The system shall provide payroll cost reports.

HRMS-FR-053: The system shall allow report filtering by department, role, date, and employment status.

HRMS-FR-054: The system shall allow authorized users to export reports.

HRMS-FR-055: The system shall support predictive attrition analytics in later versions where enough historical data exists.

### 4.6 Compensation and Benefits

#### 4.6 Description and Priority

Compensation and Benefits manages salary structures, pay grades, bonus cycles, and benefits enrollment such as health insurance and allowances.

Priority: Medium

#### 4.6 Stimulus/Response Sequences

- Assign Employee to Pay Grade: HR Officer opens employee compensation profile, selects pay grade, and the system validates and stores the compensation history.

#### 4.6 Functional Requirements

HRMS-FR-056: The system shall allow authorized users to define salary structures.

HRMS-FR-057: The system shall allow authorized users to define pay grades.

HRMS-FR-058: The system shall store compensation history.

HRMS-FR-059: The system shall manage bonus cycles.

HRMS-FR-060: The system shall manage employee allowances.

HRMS-FR-061: The system shall manage benefits enrollment.

HRMS-FR-062: The system shall restrict compensation data to authorized users.

### 4.7 Leave Management

#### 4.7 Description and Priority

Leave Management allows employees to request leave, routes approvals through managers, tracks balances by leave type, and enforces policy rules.

Priority: Medium

#### 4.7 Stimulus/Response Sequences

- Submit Leave Request: Employee logs in, selects leave type, enters start date, end date, and reason, and the system validates balance and routes the request to the manager.
- Approve Leave Request: Manager reviews leave details, approves or rejects the request, and the system updates the leave status and balance where applicable.

#### 4.7 Functional Requirements

HRMS-FR-063: The system shall allow employees to request leave. *(Canonical; HRMS-FR-029, §4.3, restates this requirement and is not a second one.)*

HRMS-FR-064: The system shall allow managers to approve or reject leave requests. *(Canonical; HRMS-FR-031, §4.3, restates this requirement and is not a second one.)*

HRMS-FR-065: The system shall track leave balances by leave type.

HRMS-FR-066: The system shall support annual leave, sick leave, maternity leave, study leave, and other company-defined leave types.

HRMS-FR-067: The system shall enforce leave policy rules.

HRMS-FR-068: The system shall prevent leave requests beyond available balance unless policy allows.

HRMS-FR-069: The system shall update leave balances after approved leave.

HRMS-FR-070: The system shall maintain leave history.

HRMS-FR-071: The system shall provide a leave calendar for HR and managers.

---

## 5. Other Nonfunctional Requirements

### 5.1 Performance Requirements

HRMS-NFR-001 to HRMS-NFR-004 state response times at the 95th percentile of requests, measured at the application server boundary and therefore excluding client network transit, over a rolling 60-minute measurement window, at the concurrent load stated in HRMS-NFR-006. The data volumes against which they are verified are TBD-016.

HRMS-NFR-005 is not a request response time and the preceding sentence does not govern it. It states the elapsed time of a single payroll run, a background operation whose duration is measured per run rather than as a percentile over a population of requests. It is verified against every run, at the concurrent load stated in HRMS-NFR-006 and the organization size stated in TBD-016.

HRMS-NFR-001: The system shall load common pages within 4 seconds at the 95th percentile.

HRMS-NFR-002: The system shall return standard employee search results within 3 seconds at the 95th percentile, over the employee record volume stated in TBD-016.

HRMS-NFR-003: Employee profile pages shall load within 3 seconds at the 95th percentile.

HRMS-NFR-004: Reports should load within 10 seconds at the 95th percentile, over the data volume stated in TBD-016.

HRMS-NFR-005: Payroll processing should complete within the elapsed time stated in TBD-017, measured from submission of a payroll run to availability of its payslips and bank transfer file, for the organization size stated in TBD-016.

HRMS-NFR-006: The system should support 200 concurrent users in the first version, sustaining HRMS-NFR-001 to HRMS-NFR-005 at that load.

HRMS-NFR-007: File uploads should support PDF, JPG, PNG, and DOCX formats.

HRMS-NFR-008: File upload size should be limited to 5MB to 10MB per document unless changed by system configuration.

### 5.2 Safety Requirements

HRMS-NFR-009: The system shall prevent unauthorized modification of payroll data.

HRMS-NFR-010: The system shall prevent ordinary users from deleting payroll history.

HRMS-NFR-011: The system shall validate critical HR and payroll inputs before saving.

HRMS-NFR-012: The system shall maintain backups to reduce the risk of data loss.

HRMS-NFR-013: The system shall record audit logs for sensitive actions.

### 5.3 Security Requirements

HRMS-NFR-014: The system shall require authentication before access.

HRMS-NFR-015: The system shall use secure password hashing.

HRMS-NFR-016: The system shall enforce role-based access control.

HRMS-NFR-017: Employees shall only access their own personal records and payslips.

HRMS-NFR-018: Managers shall only access team data assigned to them.

HRMS-NFR-019: Payroll data shall only be accessible to authorized payroll users.

HRMS-NFR-020: The system shall use HTTPS in production.

HRMS-NFR-021: Uploaded documents shall be stored securely.

HRMS-NFR-022: The system shall log login attempts, record changes, payroll actions, approvals, and permission changes.

HRMS-NFR-023: Sessions shall expire after a defined period of inactivity.

HRMS-NFR-024: The system shall require multi-factor authentication for administrators and payroll users on every authentication. The second factor shall be bound to the individual account holder and shall not be enrolled, reset, disabled, or bypassed by any role that administers user accounts, credentials, roles, or permissions. Enrollment shall be performed by the account holder, and recovery of a lost or unavailable second factor shall require approval by a user who does not administer user accounts or credentials; resetting an account's password shall not by itself restore access to an account whose second factor is enrolled. Second-factor enrollment, recovery, disablement, and failed presentation shall be logged.

### 5.4 Software Quality Attributes

#### 5.4.1 Usability

HRMS-NFR-025: The system shall provide a clean and professional user interface.

HRMS-NFR-026: The system shall use clear labels, menus, forms, and validation messages.

HRMS-NFR-027: The system shall be usable by non-technical HR staff and employees.

#### 5.4.2 Reliability

HRMS-NFR-028: The system shall save HR transactions reliably without data loss.

HRMS-NFR-029: The system shall maintain data consistency across employee, payroll, leave, and reporting modules.

#### 5.4.3 Maintainability

HRMS-NFR-030: The system shall be developed using modular architecture.

HRMS-NFR-031: The system shall follow consistent coding and naming standards.

HRMS-NFR-032: The system shall allow future modules to be added without major system redesign.

#### 5.4.4 Scalability

HRMS-NFR-033: The system shall support growth in employee records, payroll history, reports, and document storage.

HRMS-NFR-034: The system should support future integration with mobile apps and external systems.

#### 5.4.5 Availability

HRMS-NFR-035: The system should target 95% to 98% availability during working hours for the first version.

HRMS-NFR-036: Planned maintenance should be communicated in advance.

### 5.5 Business Rules

HRMS-BR-001: Every employee must have a unique employee ID.

HRMS-BR-002: Every employee must belong to a department.

HRMS-BR-003: Every employee must have one employment status.

HRMS-BR-004: Every employee should have a reporting manager unless they belong to top management.

HRMS-BR-005: Only authorized HR users can create or modify employee master records.

HRMS-BR-006: Employees can only view their own payslips.

HRMS-BR-007: Managers can only view employees assigned to them.

HRMS-BR-008: Payroll cannot be finalized without approval from an authorized user.

HRMS-BR-009: Leave requests must follow the approval workflow.

HRMS-BR-010: Approved leave must reduce the employee's leave balance.

HRMS-BR-011: Rejected leave must not reduce the employee's leave balance.

HRMS-BR-012: Terminated, resigned, or retired employees shall not access the self-service portal unless explicitly allowed by policy.

HRMS-BR-013: Candidate records shall not become employee records until the offer is accepted and onboarding is initiated.

HRMS-BR-014: Sensitive HR and payroll data shall only be visible to authorized roles.

HRMS-BR-015: Critical actions shall be logged for audit purposes.

---

## 6. Other Requirements

### 6.1 Data Requirements

- Employee
- Department
- Job title
- Role
- Reporting relationship
- Employment history
- Compensation record
- Employee document
- Emergency contact
- Job requisition
- Job posting
- Candidate
- Interview
- Offer letter
- Onboarding checklist
- Payroll record
- Payslip
- Allowance
- Deduction
- Leave request
- Leave balance
- Leave type
- Benefit
- Pay grade
- Audit log
- User account
- Permission

### 6.2 Data Validation Rules

HRMS-DR-001: Employee ID must be unique.

HRMS-DR-002: Email address must be unique.

HRMS-DR-003: Date of birth must be a valid past date.

HRMS-DR-004: Employment start date must be valid.

HRMS-DR-005: Salary values must not be negative.

HRMS-DR-006: Leave end date cannot be earlier than leave start date.

HRMS-DR-007: Required fields must be completed before submission.

HRMS-DR-008: Uploaded files must match allowed file formats.

HRMS-DR-009: Payroll records must be linked to active employee records.

HRMS-DR-010: Changes to salary and compensation should be stored as history.

### 6.3 Legal and Compliance Requirements

- Ghana payroll and statutory deduction requirements.
- Organizational HR policies.
- Data protection and privacy principles.
- Internal audit requirements.
- Employment record retention policies.

Exact legal and regulatory requirements shall be confirmed with qualified HR, legal, payroll, and finance professionals before go-live.

### 6.4 Out-of-Scope Features

- Biometric attendance integration.
- Facial recognition attendance.
- Advanced AI recruitment screening.
- Full learning management system.
- Full performance appraisal system.
- Complex shift scheduling.
- Full ERP integration.
- Full accounting system integration.
- Automatic tax filing with government portals.
- Direct integration with all Ghanaian banks.
- Employee loan management.
- Travel and expense management.
- Disciplinary case management.
- Union management.
- Multi-country payroll.
- Chatbot support.
- Full native mobile application if the first release is web-first.

---

## Appendix A: Glossary

| Term | Meaning |
|---|---|
| HRMS | Human Resource Management System |
| SRS | Software Requirements Specification |
| Core HR | The main employee record management module |
| ATS | Applicant Tracking System |
| PAYE | Pay As You Earn tax deduction |
| SSNIT | Social Security and National Insurance Trust |
| Tier 1 | Mandatory basic national pension contribution |
| Tier 2 | Mandatory occupational pension contribution |
| Tier 3 | Voluntary provident or personal pension contribution |
| RBAC | Role-Based Access Control |
| ESS | Employee Self-Service |
| MSS | Manager Self-Service |
| KPI | Key Performance Indicator |
| TBD | To Be Determined |

## Appendix B: Analysis Models

### B.1 High-Level Module Structure

```
Human Resource Management System
|
|-- Phase 1
|   |-- Core HR
|   |-- Recruitment and Onboarding
|
|-- Phase 2
|   |-- Employee Self-Service
|   |-- Manager Self-Service
|   |-- Payroll
|
|-- Phase 3
    |-- Reporting and Analytics
    |-- Compensation and Benefits
    |-- Leave Management
```

### B.2 High-Level User Access Model

```
System Administrator -> User Accounts, Roles, Permissions, Audit Logs
HR Administrator -> Employee Records, Recruitment, Onboarding, Reports
Recruiter -> Job Requisitions, Applicants, Interviews, Offers
Employee -> Own Profile, Payslips, Leave Requests
Manager -> Team Data, Approvals, Team Reports
Payroll Officer -> Payroll, Payslips, Deductions, Bank Files
Executive -> Dashboards and High-Level Reports
```

## Appendix C: To Be Determined List

| TBD ID | Description |
|---|---|
| TBD-001 | Final organization name |
| TBD-002 | Final technology stack |
| TBD-003 | Hosting environment |
| TBD-004 | Database technology |
| TBD-005 | Final payroll statutory rates |
| TBD-006 | Bank transfer file format |
| TBD-007 | HR approval workflows |
| TBD-008 | Leave policy rules |
| TBD-009 | Document retention policy |
| TBD-010 | Exact user roles and permissions |
| TBD-011 | Whether mobile app is required in first release |
| TBD-012 | Whether external job board integration is required |
| TBD-013 | Whether biometric attendance integration will be added later |
| TBD-014 | Reporting dashboard KPIs |
| TBD-015 | Data migration approach |
| TBD-016 | Organization size and data volumes against which HRMS-NFR-001 to HRMS-NFR-005 are verified: employee record count, payroll history volume, and document storage volume. Depends on TBD-001 |
| TBD-017 | Payroll processing elapsed time threshold for HRMS-NFR-005. Depends on TBD-016 |
