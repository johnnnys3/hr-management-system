# ADR-0008: Ant Design as the UI component library

**Status:** Accepted
**Date:** 2026-07-15

## Context

The HRMS interface is dominated by forms, data tables, approval queues, and role-specific dashboards. SRS §3.1 requires clean, professional, easily navigated screens with clear labels and validation messages, search and filter where necessary, and consistent buttons, tables, forms, menus, and status labels. HRMS-NFR-025 to HRMS-NFR-027 require a clean professional interface usable by non-technical staff.

The visual target was established by reference: a restrained enterprise dashboard — flat, border-defined cards with small corner radius and no shadow, a single accent colour, dense tables with light horizontal rules and uppercase column headers, segmented controls, and compact inline sparklines.

Four options were evaluated.

## Decision

**Ant Design** is the component library, themed to the established visual target using Ant Design's design token system.

Forms use **Ant Design's own Form component**. A separate form state library is not introduced.

## Consequences

**Positive**

- Ant Design is built for enterprise administrative interfaces, which is precisely the shape of this system. Table sorting, filtering, pagination, and export are provided rather than assembled.
- The visual target is within Ant Design's native register. Achieving it is a matter of theme tokens — accent colour, corner radius, shadow removal — not of fighting the library.
- Form validation, layout, and error display are integrated with the component set.
- Build effort is directed toward payroll correctness, access control, and documentation rather than toward reconstructing table and form primitives.

**Negative**

- The visual result will be recognisably Ant Design in places, despite theming. A fully bespoke aesthetic is not achievable without substantial override.
- Bundle size is significant relative to a minimal component set.
- Committing to a library's conventions constrains later visual direction. A change of aesthetic target would be costly.

**Rejected alternatives**

- *Material UI.* The most widely adopted React component library. Rejected on a specific ground: capable data grid features — filtering, sorting, export — sit behind the paid MUI X Pro licence. This system is table-heavy across every module, so that boundary would be reached early, forcing either licence purchase or reconstruction of the grid.
- *shadcn/ui with Tailwind and TanStack Table.* Component code is owned in-repo, permitting any visual target and aligning well with the extractability goal. Rejected because the chosen visual target does not require it, and the assembly cost across the module set is not repaid.
- *Mantine.* A reasonable middle option — complete, free, less visually opinionated. Ant Design was preferred for stronger table and form coverage in an administrative context.

## Note on visual references

The visual target was drawn from design concept work. Such references depict a single composed screen with ideal data. They do not address empty states, error states, validation messaging, long tables, pagination boundaries, keyboard navigation, or assistive technology support. The SRS requires a clean, professional, usable interface, not a promotional one. Reference material informs the aesthetic; it does not set the scope.
