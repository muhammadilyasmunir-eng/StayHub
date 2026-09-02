# StayHub Property Registration Complete Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a complete, browser-first seven-step StayHub property registration flow with real file uploads, complete property/policy/room/document/owner data, review, validation, pending verification, and admin approval readiness.

**Architecture:** Keep the existing FastAPI + SQLAlchemy registration contract. The public registration page collects structured data and uploads files through `/uploads/registration`; uploaded paths are then submitted through `/users/owner-register`. Registration remains Pending Verification until admin approval.

**Tech Stack:** FastAPI, Pydantic, SQLAlchemy, PostgreSQL, vanilla HTML/CSS/JavaScript, multipart uploads, pytest.

**Spec:** StayHub property-registration requirements defined in the project conversation and master architecture.

## Global Constraints

- Do not use user-entered photo/document URLs; use actual file inputs and the existing upload API.
- Support multiple hotel photos, room photos, and verification documents.
- Require exactly one primary hotel photo and exactly one primary photo per room.
- Keep the existing backend OwnerRegistration contract aligned with the frontend payload.
- Preserve Pending Verification until StayHub Admin approves the property.
- Validate exact fields and show actionable errors.
- Verify with automated tests before declaring the feature complete.

---

## Tasks

- [ ] Create the canonical seven-step registration UI.
- [ ] Add complete owner, property, facility, policy, photo, room, document, and review fields.
- [ ] Implement real multi-file uploads and previews.
- [ ] Implement room category repeaters with facilities, extra-bed data, and photos.
- [ ] Implement verification-document repeaters with license/registration/document numbers and attachments.
- [ ] Implement complete review and exact client-side validation.
- [ ] Align the public route with the canonical registration page.
- [ ] Add/extend registration contract tests for upload metadata and required sections.
- [ ] Run the full API test suite and browser/UI verification locally.
