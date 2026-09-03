# Guest Reviews Implementation Plan

## Goal
Add a complete reservation-based guest review workflow across customer, public hotel pages, owner portal, and StayHub admin.

## Data model
- Create `GuestReview` with one row per reservation (unique reservation_id), customer/guest/hotel ownership, overall score, category scores, written text, owner reply, created/updated timestamps, guest-edit deadline, soft-delete timestamp/state.
- Keep a deleted review row so a customer cannot create a second review for the same reservation.

## API
- Customer: list own reviews, create review only after checkout and only once, edit within 7 days, soft-delete after the edit window or earlier.
- Owner: list property reviews and optionally reply/edit reply.
- Admin: list all reviews, edit review content/scores, soft-delete/delete reviews.
- Public: list published non-deleted reviews for an approved hotel with aggregate/category scores and reviewer metadata.

## Customer UI
- Add Review action to My Reservations.
- Active after checkout; after submission show the customer's review and edit/delete controls.
- Edit is available for 7 days; after that only delete remains. Deleted reviews cannot be resubmitted.

## Owner UI
- Replace the placeholder Reviews workspace with review cards, ratings/categories, guest text, and optional reply controls.

## Admin UI
- Replace the placeholder Reviews workspace with moderation table/detail, edit, and delete controls.

## Public UI
- Add a Booking.com-style Guest reviews section to the public hotel page with overall score, category scores, review count, filters/sorting, and review cards including owner replies.

## Verification
- Run Python compile checks and API/UI smoke checks locally where available.
- Verify customer eligibility, one-review rule, 7-day edit boundary, delete lockout, owner replies, admin moderation, and public aggregation.
