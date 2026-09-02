# StayHub Property/Admin/Reservations/Finance Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add persistent property operational fields, full StayHub Admin property/owner management, daily reservations reporting, and post-checkout finance/commission reporting without breaking the existing three-area StayHub architecture.

**Architecture:** Extend the existing FastAPI + SQLAlchemy backend and existing public/admin HTML/JS UI patterns. Keep one source of truth for property, reservation and financial state; expose admin-only mutation/reporting endpoints and consume them from dashboard/sidebar screens.

**Tech Stack:** Python 3.12, FastAPI, SQLAlchemy, PostgreSQL, existing HTML/CSS/JavaScript, pytest.

**Spec:** `docs/superpowers/specs/2026-08-24-property-admin-reservations-finance-design.md`

## Global Constraints

- Preserve Public Website, StayHub Admin, and Hotel Owner Portal as distinct connected areas.
- Existing property registration fields must remain available.
- Passwords are never displayed; only secure reset functionality is exposed.
- Admin-only operations must enforce authorization server-side.
- Financial totals must be calculated from persisted booking data server-side.
- Test UI flows through browser/UI where practical; use backend tests for invariants.

---

### Task 1: Property registration data model and migration

**Files:**
- Modify: existing Hotel/property model and registration schema/service files identified from current repository structure.
- Create: database migration for payment methods, parking floors, breakfast options/custom text, and property-highlight floors.
- Test: property model/schema contract tests.

- [ ] Write failing tests proving each new field can be persisted and returned.
- [ ] Run the focused tests and verify failure.
- [ ] Add normalized/persisted fields using the repository's existing migration conventions.
- [ ] Update registration schemas/services to accept and validate the fields.
- [ ] Run focused tests and verify pass.
- [ ] Commit the task.

### Task 2: Registration UI controls

**Files:**
- Modify: existing owner registration HTML/JS.
- Test: registration flow contract/UI tests.

- [ ] Add checkbox controls for Cash, Credit Card and Debit Card.
- [ ] Add multi-select parking floors supporting Ground/Basement and 1–200.
- [ ] Add breakfast checkboxes for Continental, American, Asian, Buffet and Pakistani plus custom text.
- [ ] Add multi-select property-highlight floors 1–200.
- [ ] Ensure controls serialize into the registration payload.
- [ ] Test the UI contract and backend submission.
- [ ] Commit the task.

### Task 3: Admin property status dashboard/sidebar

**Files:**
- Modify: existing admin dashboard/sidebar HTML/JS.
- Modify: existing admin property service/routes.
- Test: admin property status aggregation tests.

- [ ] Add failing tests for Active, Pending, Rejected, Invoice Overdue and Duplicate Rejection counts/lists.
- [ ] Implement server-side status queries.
- [ ] Add dashboard cards and matching sidebar tabs.
- [ ] Wire each card/tab to its filtered property list.
- [ ] Test counts and filters.
- [ ] Commit the task.

### Task 4: Full pending-property admin edit

**Files:**
- Modify: admin property schemas/routes/services.
- Modify: admin property edit UI.
- Test: admin authorization and full-edit tests.

- [ ] Write tests that an admin can edit pending property fields and non-admin users cannot.
- [ ] Implement full edit payload covering registration fields, rooms, photos, facilities, policies, rates and documents using existing models/services.
- [ ] Add Save Changes, Approve and Reject actions.
- [ ] Ensure edits persist before approval.
- [ ] Run focused tests.
- [ ] Commit the task.

### Task 5: Admin owner details and password reset

**Files:**
- Modify: existing user/admin routes and admin UI.
- Test: owner-detail and reset authorization/security tests.

- [ ] Add tests for email, mobile and username display and password non-disclosure.
- [ ] Reuse/create secure password-reset workflow with one-time token behavior.
- [ ] Add Reset Password action to property owner details.
- [ ] Verify admin authorization.
- [ ] Commit the task.

### Task 6: Admin property deletion

**Files:**
- Modify: admin property route/service.
- Modify: admin property UI.
- Test: deletion authorization and dependent-data behavior.

- [ ] Write failing tests for admin-only deletion and confirmation-required UI behavior.
- [ ] Implement server-side deletion using existing SQLAlchemy cascades/relationships where safe.
- [ ] Ensure related owner/property records are handled according to the intended property ownership rules rather than accidentally deleting unrelated users.
- [ ] Add confirmation UI and refresh counts/lists after deletion.
- [ ] Run tests.
- [ ] Commit the task.

### Task 7: Reservations admin tab and daily reporting

**Files:**
- Modify: existing reservation models/services/routes as needed.
- Create/modify: admin reservations UI.
- Test: daily reservation aggregation tests.

- [ ] Add tests for date-filtered reservation count, gross revenue and commission per hotel and globally.
- [ ] Implement server-side aggregation.
- [ ] Add Reservations sidebar tab and dashboard entry.
- [ ] Add date filter and hotel-wise breakdown.
- [ ] Verify empty dates and multiple hotels.
- [ ] Commit the task.

### Task 8: Finance post-checkout reporting

**Files:**
- Modify: finance service/routes.
- Modify: admin finance UI.
- Test: checkout-date inclusion and commission/revenue tests.

- [ ] Write tests proving a confirmed booking before checkout is excluded from completed finance and included after checkout.
- [ ] Implement completed-stay query using reservation checkout date and persisted financial values.
- [ ] Show guest, hotel, dates, booking amount, hotel revenue, StayHub commission, payment and invoice status.
- [ ] Add finance filters and totals.
- [ ] Run focused finance tests.
- [ ] Commit the task.

### Task 9: End-to-end regression and UI verification

**Files:**
- Modify: tests only as needed for regressions.

- [ ] Run the complete backend test suite.
- [ ] Start the application locally.
- [ ] Test registration in browser: fields → property type → new fields → submit.
- [ ] Test Admin dashboard cards/sidebar.
- [ ] Test pending property full edit and approve/reject.
- [ ] Test owner details and reset-password action.
- [ ] Test property deletion.
- [ ] Test Reservations daily report.
- [ ] Test Finance after checkout.
- [ ] Fix any failures using systematic debugging.
- [ ] Run final verification before claiming completion.
- [ ] Commit the completed implementation.
