# Complete Property Registration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a complete seven-step StayHub property registration wizard with categorized multi-photo uploads, complete rooms, documents, review, and stable navigation.

**Architecture:** Keep `owner-register-v4.html` as one self-contained page with a single step controller. Dynamic photo, room, and document entries are stored in the DOM and transformed into structured review/submission data.

**Tech Stack:** HTML, CSS, vanilla JavaScript, FastAPI backend, existing upload endpoint and OwnerRegistration schema.

**Spec:** `docs/superpowers/specs/2026-08-21-complete-property-registration-design.md`

## Global Constraints
- Exactly seven wizard steps.
- One navigation controller only.
- Real file inputs, never manually entered photo/document URLs.
- Property and room photos require names.
- Multiple photos per category are allowed.
- Review never displays passwords.

---

### Task 1: Expand the wizard data model and stable navigation

**Files:**
- Modify: `apps/api/app/static/public/owner-register-v4.html`

- [ ] Replace short-form step markup with complete owner, property, policy, photo, room, document, and review sections.
- [ ] Keep `show(step)`, `next`, and `prev` as the only navigation path.
- [ ] Validate only the active step before moving forward.
- [ ] Rebuild review every time step 7 opens.

### Task 2: Implement categorized property photo entries

**Files:**
- Modify: `apps/api/app/static/public/owner-register-v4.html`

- [ ] Add multi-file selection.
- [ ] Create one editable metadata card per selected file.
- [ ] Require photo name and category.
- [ ] Support exactly one primary property photo.
- [ ] Support unlimited/reasonable multiple photos for the same category.

### Task 3: Implement complete room categories and room photos

**Files:**
- Modify: `apps/api/app/static/public/owner-register-v4.html`

- [ ] Add all room fields required by OwnerRegistration.
- [ ] Add selectable room facilities.
- [ ] Add extra-bed controls.
- [ ] Add multi-photo room uploads with required names and primary selection.

### Task 4: Implement complete verification documents and review

**Files:**
- Modify: `apps/api/app/static/public/owner-register-v4.html`

- [ ] Add complete document metadata and file upload.
- [ ] Build section-based review with Edit buttons.
- [ ] Exclude passwords from review.

### Task 5: Verify existing backend contract

**Files:**
- Test: `apps/api/tests/test_owner_registration_contract.py`

- [ ] Run `python -m pytest -q tests`.
- [ ] Confirm all contract tests pass.
- [ ] Use the browser to verify 1→7 and Previous navigation after pull.