# StayHub Three-Portal Architecture Design

## Goal
Organize the existing StayHub platform into three clearly separated areas while preserving the existing backend/domain work.

## Areas

### 1. Public Website
Purpose: customer-facing hotel marketplace.

Responsibilities:
- Search and browse approved properties
- View property details, rooms, rates, photos and policies
- Booking/customer flows
- Reviews
- Property registration entry point: List Your Property

### 2. StayHub Admin Panel
Purpose: internal StayHub platform administration.

Responsibilities:
- Dashboard
- Receive property registration requests
- Review and verify property information/documents
- Approve or reject properties
- Publish/unpublish approved properties on the public marketplace
- Manage users/properties and platform-level reservations/reviews as supported by existing backend

### 3. Hotel Owner Portal
Purpose: hotel/property management after owner registration and approval.

Responsibilities:
- Owner authentication
- Property profile
- Rooms and room types
- Photos, rates and availability
- Calendar
- Reservations
- Guests
- Room allocation
- Inbox/messages
- Reviews
- Finance/invoices

## Property Lifecycle
1. Owner selects List Your Property on the public website.
2. Owner creates credentials and submits property information.
3. Submission is stored as a pending property-registration request.
4. Admin reviews and verifies the request.
5. Admin approves or rejects it.
6. Approved property becomes eligible for public marketplace listing.
7. Owner can manage the approved property through the owner portal.

## Routing
The preferred URL structure is:
- Public: `/`
- Admin: `/admin`
- Owner: `/owner`

The actual host/port must follow the existing frontend application rather than inventing a second application or service.

## Constraints
- Existing backend/domain models and APIs must be reused where applicable.
- Do not create a parallel unrelated project.
- Do not delete working hotel/property functionality merely to create routes.
- Public listings must be controlled by admin approval/publication state.
- Owner credentials must not be exposed to the public marketplace.
- UI testing should be preferred over Swagger/API-only verification wherever practical.
