# StayHub Three-Portal Architecture Design

## Goal

StayHub will operate as one platform with three distinct user-facing areas: Public Website, StayHub Admin Panel, and Hotel Owner Portal.

## Responsibilities

### Public Website
Customers search approved hotels/properties, view rooms/rates/details, and use the supported booking/review flows.

### StayHub Admin Panel
StayHub staff review property-registration requests, verify submitted information, approve/reject properties, and control whether approved properties are publicly listed.

### Hotel Owner Portal
Property owners manage their approved property, rooms/room types, reservations, guests, rates, availability/calendar, reviews, messages, and finance features supported by the current backend.

## Core Lifecycle

1. Owner submits a property through List Your Property.
2. Submission is stored as pending/unapproved.
3. StayHub Admin reviews the property.
4. Admin approves or rejects it.
5. Only approved/published properties appear on the Public Website.
6. Approved owner uses the Owner Portal for ongoing hotel operations.

## Routing Principle

Use separate frontend routes/entry points for Public, Admin, and Owner experiences. Exact route names and ports must follow the repository's existing frontend framework and scripts; do not invent a second application when an existing route can be normalized.

## Existing Backend Reuse

The repository already contains administrative hotel APIs, public hotel APIs, hotel operations APIs, reservation APIs, room APIs, and room-type APIs. The frontend should consume these existing interfaces rather than duplicating domain logic.

## Acceptance Criteria

- Public, Admin, and Owner experiences are independently reachable.
- Admin can review and decide property submissions.
- Approval controls public visibility.
- Owner can access hotel operations without entering Admin UI.
- Customers cannot access Owner/Admin operational screens.
- Existing backend property/room/reservation work remains intact.
- Browser/UI verification covers the critical registration-to-public-listing lifecycle.
