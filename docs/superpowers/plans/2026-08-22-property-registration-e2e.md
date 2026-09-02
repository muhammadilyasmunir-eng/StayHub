# Property Registration End-to-End Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the seven-step property registration UI upload files, persist the complete registration, support admin approval, and expose only approved properties publicly.

**Architecture:** Keep the existing FastAPI/PostgreSQL domain models and registration service. Add a browser-side submission client that uploads files first, then posts the existing `OwnerRegistration` contract. Use existing admin approval APIs and add a public read-only API filtered to approved properties.

**Tech Stack:** FastAPI, SQLAlchemy, PostgreSQL, Pydantic, Alembic, vanilla HTML/JavaScript, pytest.

**Spec:** Saved StayHub master architecture and current owner registration requirements.

## Global Constraints

- Preserve the existing seven-step navigation.
- Test workflows through browser UI where practical.
- Property status must remain `pending` until admin approval.
- Pending, rejected, suspended, and inactive properties must not be exposed through public property routes.
- Multiple photos and documents must use actual file upload, not pasted URLs.

---

### Task 1: Browser file upload and registration submission

**Files:**
- Create: `apps/api/app/static/public/owner-register-submit.js`
- Modify: `apps/api/app/static/public/owner-register.html`

**Interfaces:**
- Consumes: `POST /uploads/registration`
- Produces: `POST /users/owner-register` payload matching `OwnerRegistration`

- [x] Capture property, room, and document files from the seven-step UI.
- [x] Upload each file and collect returned static URLs.
- [x] Build the registration JSON payload with facilities, policies, photos, rooms, and documents.
- [x] Submit the payload and render backend validation errors or pending confirmation.

### Task 2: Admin verification UI

**Files:**
- Verify: `apps/api/app/static/public/admin-properties.html`
- Verify: `apps/api/app/api/admin/hotels.py`

**Interfaces:**
- Consumes: authenticated admin token and pending hotel endpoints.
- Produces: approve or reject state changes.

- [x] Verify the UI renders owner, property, facilities, policies, photos, documents, and room categories.
- [x] Verify approve/reject controls call the protected admin endpoints.

### Task 3: Public approved-property API

**Files:**
- Create: `apps/api/app/api/public_hotels.py`
- Modify: `apps/api/app/api/routes.py`

**Interfaces:**
- Produces: `GET /public/hotels/` and `GET /public/hotels/{slug}`.

- [x] Filter all public listing queries to `HotelStatus.APPROVED`.
- [x] Expose public-safe property summary, primary photo, facilities, and detailed room/photo data.
- [x] Return 404 for non-approved property slugs.

### Task 4: Browser end-to-end verification

**Files:**
- Test: `apps/api/tests/`

- [ ] Start the local API and submit a new property through the browser.
- [ ] Confirm uploaded files are reachable under `/static/uploads/`.
- [ ] Confirm the property is pending in the admin UI.
- [ ] Approve the property and confirm it appears from `/public/hotels/`.
- [ ] Reject a second property and confirm it remains absent from public results.
- [ ] Run the full pytest suite and fix any failures before declaring completion.
