# Owner Approval & Terms Acceptance Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a versioned Terms & Conditions acceptance gate between Admin approval and public property publication while preserving owner records across all property status changes.

**Architecture:** Extend the existing Hotel approval workflow with an `approved-awaiting-terms` state (or equivalent explicit publication gate), persistent T&C assignment/acceptance metadata, admin upload/selection, owner notification, and owner acceptance endpoints/UI. Keep User/Owner as the durable identity and Hotel as the independently changing property record.

**Tech Stack:** FastAPI, SQLAlchemy, existing StayHub static HTML/JS admin and owner portals, existing database migration system/storage conventions.

**Spec:** `docs/superpowers/specs/2026-08-27-owner-approval-terms-design.md`

## Global Constraints

- Owner/User records must never be deleted merely because a property is rejected.
- One owner may have multiple properties.
- T&C acceptance is property-specific and version-specific.
- Approved-awaiting-terms properties must not appear in the public marketplace.
- Existing reject/edit/resubmit workflows must continue to work.
- Test through UI/pages wherever practical rather than Swagger/API-only testing.

---

### Task 1: Data model and migration

**Files:**
- Modify: `apps/api/app/models/hotel.py`
- Create/modify: database migration under the repository's existing Alembic versions directory
- Create/modify: T&C/notification model files if existing conventions require separate tables

**Interfaces:**
- Produces persistent property approval/T&C assignment and acceptance state.

- [ ] Add explicit property publication/terms state and fields for assigned T&C document URL, filename/version, assigned admin, assigned timestamp, acceptance owner and acceptance timestamp.
- [ ] Add a durable T&C document/version model if the existing storage pattern requires it.
- [ ] Add notification persistence if no suitable existing notification model exists.
- [ ] Ensure User deletion is not triggered by Hotel rejection; preserve existing owner relationship semantics for normal user lifecycle.
- [ ] Add migration(s) with safe defaults for existing hotels.
- [ ] Run model/import and migration tests.
- [ ] Commit.

### Task 2: Admin approval and T&C attachment API

**Files:**
- Modify: `apps/api/app/api/admin/hotels.py`
- Modify/create: admin schemas/services as needed
- Modify/create: existing file upload/storage route as needed

**Interfaces:**
- Admin approve operation accepts an active T&C document/version and does not publish immediately.
- Owner-facing property endpoint can retrieve its assigned T&C safely.

- [ ] Add admin T&C upload/select endpoint using the project's existing file storage convention.
- [ ] Change approval to require/select a T&C version.
- [ ] Set property to approved-awaiting-terms and record audit metadata.
- [ ] Ensure public listing queries exclude approved-awaiting-terms.
- [ ] Preserve rejection/edit/resubmit behavior.
- [ ] Add API tests for approval gate, missing T&C, and public exclusion.
- [ ] Commit.

### Task 3: Owner notification and T&C acceptance API

**Files:**
- Modify/create: owner API routes/services
- Modify/create: notification model/schema/service

**Interfaces:**
- Owner can list/read notifications.
- Owner can retrieve the assigned T&C for their property.
- Owner can accept and submit a specific T&C version exactly once per submission.

- [ ] Create approval notification tied to the owner and property.
- [ ] Add owner endpoint for pending T&C acceptance.
- [ ] Add accept endpoint validating current authenticated owner and assigned document/version.
- [ ] Record acceptance timestamp, owner, property, document/version.
- [ ] Transition property to live/approved-public only after successful acceptance.
- [ ] Reject unauthorized cross-owner access.
- [ ] Add tests for notification, acceptance, duplicate acceptance, and authorization.
- [ ] Commit.

### Task 4: Admin Portal UI

**Files:**
- Modify: `apps/api/app/static/admin-panel.html`
- Modify/create: admin property operation JS

**Interfaces:**
- Approve flow asks admin to attach/select T&C and shows awaiting-owner status.

- [ ] Add T&C attachment control to approval dialog.
- [ ] Show filename/version before approval confirmation.
- [ ] Show `Approved - Awaiting Owner T&C Acceptance` status.
- [ ] Show owner acceptance state/timestamp when available.
- [ ] Keep existing Edit/Reject/Photo controls unchanged.
- [ ] Test through `/admin` UI.
- [ ] Commit.

### Task 5: Owner Portal UI

**Files:**
- Modify: `apps/api/app/static/owner-portal-pro.html`
- Modify/create: owner notification/T&C JS

**Interfaces:**
- Owner sees approval notification and an in-portal T&C reader with explicit acceptance.

- [ ] Add notification badge/card for T&C required.
- [ ] Add document viewer using an embedded browser-safe viewer or equivalent in-portal presentation.
- [ ] Require `I have read and agree` checkbox before enabling submit.
- [ ] Submit acceptance for the correct property/version.
- [ ] Show success state and Live/Active status only after server confirmation.
- [ ] Ensure rejected-property notices and Edit Property workflow remain intact.
- [ ] Test through Owner Portal UI.
- [ ] Commit.

### Task 6: Owner persistence and multi-property regression

**Files:**
- Modify: owner registration/service code only if current behavior can create duplicate owners or delete owners
- Add tests under the repository's existing test layout

- [ ] Register property A with owner email.
- [ ] Reject A and verify owner remains in Owners & Users.
- [ ] Register/link property B for the same owner and verify the owner identity is reused where intended.
- [ ] Approve A with T&C and verify only A gets the acceptance requirement.
- [ ] Accept A and verify A becomes live while B retains its own status.
- [ ] Verify owner data remains after every status transition.
- [ ] Commit.

### Task 7: End-to-end verification

**Files:**
- No production files unless fixes are required.

- [ ] Run backend test suite and targeted tests.
- [ ] Run the UI flow against the local application.
- [ ] Verify Admin approve → notification → T&C viewer → accept → live.
- [ ] Verify no-T&C approval is blocked.
- [ ] Verify unaccepted approved properties are absent from marketplace.
- [ ] Verify rejected property remains visible to owner with rejection reason and editable.
- [ ] Verify Owners & Users survives rejection.
- [ ] Only claim completion after verification evidence is available.
