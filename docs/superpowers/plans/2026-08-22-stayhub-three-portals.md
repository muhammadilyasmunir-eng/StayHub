# StayHub Three-Portals Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Expose the existing StayHub functionality as three clearly separated public, admin, and hotel-owner areas without discarding existing backend work.

**Architecture:** Reuse the existing API/domain layer. The frontend should route `/` to the customer marketplace, `/admin` to StayHub administration, and `/owner` to the hotel-owner management portal. Existing host/port and frontend framework must be discovered from the repository before route files are changed.

**Tech Stack:** Existing StayHub stack; do not introduce an unrelated frontend framework or second application.

**Spec:** `docs/superpowers/specs/2026-08-22-stayhub-three-portals-design.md`

## Global Constraints

- Reuse existing backend/domain APIs.
- Preserve working property registration and hotel management behavior.
- Public marketplace shows approved/published properties only.
- Admin controls property approval/rejection/publication.
- Owner portal contains hotel operations and management workflows.
- Prefer UI/browser verification over API/Swagger-only testing.

---

### Task 1: Discover the current frontend entrypoint and routing

**Files:**
- Inspect existing frontend files and package configuration in the repository.

**Steps:**
- [ ] Identify frontend application directory, framework, start command, and current routes.
- [ ] Identify which existing screen is public marketplace, which is owner operations, and whether an admin screen already exists.
- [ ] Identify shared authentication/layout components.
- [ ] Do not modify code until the actual frontend files are identified.

### Task 2: Add the three portal routes using the existing frontend

**Files:**
- Modify the repository's existing router/entrypoint only after Task 1 identifies exact paths.

**Steps:**
- [ ] Add/confirm `/` for Public Website.
- [ ] Add/confirm `/admin` for StayHub Admin.
- [ ] Add/confirm `/owner` for Hotel Owner Portal.
- [ ] Preserve existing links and redirects where possible.

### Task 3: Connect property registration to Admin review

**Steps:**
- [ ] Ensure `List Your Property` opens the registration flow.
- [ ] Ensure submit creates/updates a pending registration using the existing backend.
- [ ] Ensure the form closes or redirects after successful submission rather than remaining in a stale state.
- [ ] Ensure credentials are handled by the existing authentication flow.
- [ ] Ensure Admin can see pending submissions and approve/reject them.

### Task 4: Connect approved properties to the public marketplace

**Steps:**
- [ ] Use the existing public hotel API/data source.
- [ ] Display only properties allowed by the existing approval/publication state.
- [ ] Ensure property details and room information are reachable from the public site.

### Task 5: Connect the owner portal

**Steps:**
- [ ] Owner login redirects to `/owner`.
- [ ] Owner can access only the properties they are authorized to manage.
- [ ] Existing reservations, guests, rooms, room types, rates, availability, reviews and finance functionality is surfaced through the owner portal where already implemented.

### Task 6: UI verification

**Steps:**
- [ ] Start the existing application using its documented/current command.
- [ ] Open `/` in a browser.
- [ ] Open `/admin` in a browser.
- [ ] Open `/owner` in a browser.
- [ ] Test property registration through the UI.
- [ ] Test admin approval through the UI.
- [ ] Verify an approved property becomes visible on the public site.
- [ ] Verify owner login and owner dashboard access.

### Task 7: Commit and report

**Steps:**
- [ ] Run available frontend/backend tests.
- [ ] Check for broken imports/routes.
- [ ] Commit the implementation with a focused message.
- [ ] Report exact local URLs and the verified flow.
