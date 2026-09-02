# StayHub Final Property Review and Live Properties Design

## Goal
Implement a complete admin-controlled property lifecycle without breaking the existing stable owner submission and pending-property workflow.

## Authoritative Workflow

1. Owner registers a property.
2. Admin performs the existing initial approval/document-request stage.
3. Owner accepts all required approval documents and submits CNIC/Passport Front, CNIC/Passport Back, and Signed Agreement.
4. Submission sets the property to the admin Pending queue with `owner_documents_submitted=true`.
5. In Admin Pending Properties, the property is presented as `Ready for Final Review`, not `AWAITING_TERMS`.
6. Admin opens the property and sees the complete property profile before making a final decision.
7. Admin can choose:
   - Go For Live: property becomes `APPROVED` and is visible on the public StayHub marketplace.
   - Send Back / Reject: rejection reason is required, the owner is notified, and the property is returned to the owner correction/resubmission workflow.
8. Approved properties appear in a dedicated Live Properties admin area.

## Pending Final Review

The Pending Properties table must keep the stable pending rendering behavior and must not disappear after initial display.

For each final-review-ready property, the admin can open a complete profile containing:

- Property registration details
- Owner details
- Property type and contact details
- Address and location data
- Rooms and rates
- Facilities
- Policies
- Property photos
- Registration/original documents
- Owner CNIC/Passport Front
- Owner CNIC/Passport Back
- Signed Agreement

Document URLs must be viewable by the admin. The review page is read-only by default, with final actions separated from ordinary editing.

## Final Admin Actions

### Go For Live

Go For Live is allowed only when owner verification documents are complete. It sets the property status to `APPROVED`, records the approving admin and approval time, marks the admin-review notification handled, and sends the owner a property-live notification.

### Send Back to Owner

A reason is mandatory. The property must not become public. The reason is stored and the owner receives a notification explaining that correction/resubmission is required.

The implementation must use the existing owner correction/resubmission flow where possible instead of introducing a parallel lifecycle.

## Live Properties

Add a dedicated Live Properties dashboard card and navigation area.

Only `APPROVED` properties appear there.

Opening a live property shows the same complete profile data. Admin actions are:

- Edit Property
- Close / Deactivate Property
- Delete Property

Close/Deactivate hides the property from the public marketplace while preserving its record. Delete permanently removes the property and related data according to existing database cascade behavior and must require an explicit confirmation in the UI.

## API Boundaries

Existing admin hotel serialization remains the single complete-profile source where practical.

The verification API remains responsible for owner submission, verification queue, and final go-live validation.

The admin hotel API is extended only for lifecycle operations that belong to property management, including explicit deletion and final-review data access where required.

Avoid introducing duplicate status representations. Database enum values remain the source of truth. UI labels such as `Ready for Final Review` are presentation labels derived from submission state.

## Status Rules

- `AWAITING_TERMS`: owner is still in the document acceptance/submission stage.
- `PENDING` with `owner_documents_submitted=true`: Ready for Final Review.
- `APPROVED`: Live Property.
- `REJECTED`: requires owner correction/resubmission.
- `SUSPENDED` or closed state: hidden from marketplace but preserved.

A property that has completed owner submission must not be shown to the admin as `AWAITING_TERMS` in the final-review action area.

## Public Marketplace Rule

Only approved/live properties are visible in the public StayHub marketplace. No pending, awaiting-terms, rejected, or closed property may become public before final admin approval.

## UI Design

The admin JavaScript currently manages dashboard cards, status pages, and property lists. The implementation will extend that existing surface instead of replacing the stable pending rendering logic.

New UI behavior:

- Pending row/property opens Final Review.
- Final Review has document viewing and Go For Live / Send Back actions.
- Live Properties is separate from generic Active Properties if needed, with approved properties as its data source.
- Live property detail supports edit, close, and delete with confirmation.

## Error Handling

- Missing verification documents block Go For Live with a clear error.
- Send Back requires a non-empty reason.
- API failures keep the current profile visible and display the returned backend error.
- Refresh operations must not overwrite a populated pending list with stale or unrelated data.

## Testing

The implementation will be tested through the existing web UI where practical:

1. Owner submission appears once and remains visible in Pending.
2. Pending property displays `Ready for Final Review` when owner documents are submitted.
3. Complete property profile and all available documents can be opened by Admin.
4. Go For Live moves the property from Pending to Live Properties and public eligibility.
5. Send Back requires a reason and keeps the property non-public.
6. Live Properties displays only approved properties.
7. Close hides a property from public eligibility while preserving the record.
8. Delete requires confirmation and removes the property through the existing relationship/cascade model.
9. Existing stable Pending Properties rendering remains intact.
