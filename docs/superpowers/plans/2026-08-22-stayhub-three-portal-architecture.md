# StayHub Three-Portal Architecture Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Organize the existing StayHub project into three clearly separated areas: Public Website, StayHub Admin Panel, and Hotel Owner Portal, while preserving the existing backend property, room, reservation, and public-hotel work.

**Architecture:** Reuse the existing API/domain model and expose three frontend entry points/routes. Public users see approved properties and booking/search workflows; StayHub administrators manage property verification/publication; hotel owners manage their own property operations. Existing APIs are preferred over duplicate implementations.

**Tech Stack:** Existing StayHub repository stack; preserve current framework and dependencies discovered in the repository rather than introducing an unrelated frontend stack.

**Spec:** StayHub three-area architecture approved by the user in conversation on 2026-08-22.

## Global Constraints

- Use the existing StayHub repository as the source of truth.
- Do not replace existing backend work unnecessarily.
- Keep Public, Admin, and Owner responsibilities separate.
- Property registration must flow through Admin approval before public publication.
- Owner access must be restricted to the owner's property/data.
- Verify behavior through browser/UI where practical, not only API/Swagger.

---

### Task 1: Map existing frontend and routes

**Files:** Existing frontend files discovered in repository.

- [ ] Identify all current frontend entry points, dashboards, routes, package scripts, and ports.
- [ ] Identify the current Public Website, Hotel Operations/Owner dashboard, and any Admin UI already present.
- [ ] Map each screen to existing backend endpoints before changing code.
- [ ] Record duplicate dashboard implementations so only one Owner Portal is the canonical UI.
- [ ] Verify route behavior with the existing local development command.

### Task 2: Establish three portal entry points

**Files:** Existing router/app entry files identified in Task 1.

- [ ] Add or normalize the Public Website route.
- [ ] Add or normalize the StayHub Admin route.
- [ ] Add or normalize the Hotel Owner route.
- [ ] Ensure navigation/auth does not accidentally send owners to Admin or customers to Owner UI.
- [ ] Add route-level tests where the existing frontend test setup supports them.

### Task 3: Connect Admin property approval flow

**Files:** Existing Admin property pages/services and existing admin hotel API integration.

- [ ] Show pending property registration submissions.
- [ ] Show property details, submitted information, photos/documents where already supported.
- [ ] Implement approve/reject actions against existing API endpoints.
- [ ] Ensure approval makes the property eligible for public listing.
- [ ] Ensure rejection does not publish the property.
- [ ] Test approval and rejection through the UI.

### Task 4: Connect Owner Portal

**Files:** Existing hotel operations/dashboard pages and owner services.

- [ ] Make the canonical Owner Portal dashboard.
- [ ] Connect property management.
- [ ] Connect reservations.
- [ ] Connect guests.
- [ ] Connect rooms and room types.
- [ ] Connect rates and availability/calendar using existing backend support.
- [ ] Connect reviews, messages, and finance where existing APIs/data support them.
- [ ] Ensure owner data is scoped to the authenticated owner/property.

### Task 5: Connect Public Website

**Files:** Existing public website/search/property pages and public hotel API integration.

- [ ] Display approved/public properties only.
- [ ] Provide hotel/property search and listing pages.
- [ ] Provide property details and available room information supported by the existing backend.
- [ ] Connect booking/reservation flow using existing reservation functionality.
- [ ] Keep unapproved properties hidden from public listings.

### Task 6: End-to-end UI verification

- [ ] Start the project using the repository's documented/current development command.
- [ ] Open Public Website directly.
- [ ] Open Admin Panel directly.
- [ ] Open Owner Portal directly.
- [ ] Test property registration -> Admin review -> approval -> Public listing.
- [ ] Test Owner login -> Owner dashboard -> property/reservation/room operations.
- [ ] Fix routing, auth, API, or UI errors discovered during browser testing.
- [ ] Run the existing automated tests after UI verification.

### Task 7: Final cleanup

- [ ] Remove or redirect obsolete duplicate dashboard entry points.
- [ ] Keep clear names for Public, Admin, and Owner routes.
- [ ] Update project documentation with the three URLs/entry points.
- [ ] Verify no existing working backend endpoints were unnecessarily removed.

---
