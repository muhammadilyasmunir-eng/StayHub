# StayHub Property, Admin, Reservations & Finance Design

## Goal
Extend the existing StayHub marketplace so property registration captures operational property details, while StayHub Admin can fully manage properties, owners, reservations, revenue and commission.

## Scope
1. Property registration fields: multi-select payment methods, multi-select parking floors, breakfast types plus custom text, and property-highlight floors 1–200.
2. Admin dashboard and sidebar: Active, Pending, Rejected, Invoice Overdue, Duplicate Rejection, Reservations, Finance.
3. Pending property full edit, approve/reject, and property deletion.
4. Property owner detail view with email, mobile, username and password-reset action; never expose stored passwords.
5. Daily reservation reporting by hotel with reservation count, revenue and StayHub commission.
6. Finance reporting for completed stays after checkout, including hotel revenue and StayHub commission.

## Property Registration
Existing property fields remain. New fields are persisted, not UI-only:
- payment_methods: multiple selectable values: Cash, Credit Card, Debit Card.
- parking_floors: multiple selectable floors, supporting Ground/Basement and numbered floors through 200.
- breakfast_options: Continental, American, Asian, Buffet, Pakistani plus a custom free-text field.
- property_highlight_floors: multiple floors from 1 through 200.

## Admin
Dashboard cards and sidebar entries use the same backend query sources. Pending properties open a full edit form covering registration data, rooms, photos, facilities, policies, rates and documents. Admin may save edits, approve, reject, or delete. Deletion requires confirmation and removes/archives dependent data according to existing model relationships.

Owner details show email, mobile and username. Passwords are never displayed; reset creates the platform's existing secure password-reset flow.

## Reservations & Finance
Reservations page provides date-filtered daily totals and hotel breakdown: reservation count, gross booking revenue, hotel revenue and StayHub commission. Finance marks financial completion based on the reservation checkout date: a stay is included in completed/settled finance after checkout, with revenue and commission derived from the booking's persisted financial values rather than recomputed inconsistently in each UI.

## Architecture
Reuse existing SQLAlchemy models, FastAPI routes/services and public/admin HTML/JS patterns. Add normalized fields/tables only where necessary; use migrations for schema changes. Keep public customer, StayHub Admin and hotel-owner portals connected to the same backend and approval state.

## Security
Admin-only mutation endpoints require existing admin authorization. Password reset is tokenized/one-time and passwords remain hashed. Property deletion is admin-only and confirmed. Financial values are server-derived and not trusted from browser input.

## Testing
Add backend contract/unit tests for new fields, admin edit/delete authorization, owner reset behavior, reservation daily aggregation, and post-checkout finance inclusion. Test registration and admin workflows through browser/UI where practical; use API tests for backend invariants.
