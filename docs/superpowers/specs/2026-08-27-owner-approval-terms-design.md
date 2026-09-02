# StayHub Owner Approval & Terms Acceptance Design

## Goal
When an admin approves a property, the property must remain non-public until the owner receives the admin-selected Terms & Conditions document, reads it in the Owner Portal, accepts it, and submits the acceptance. Owner records must persist independently of property rejection.

## Flow
1. Owner registers a property using an email/account.
2. The owner/user record remains persistent and can own multiple properties.
3. Admin rejects a property without deleting the owner/user record.
4. Admin approves a property by selecting/attaching a Terms & Conditions document/version.
5. Approval changes the property to an approved-awaiting-terms state, not public/live.
6. Owner Portal shows a notification and the attached Terms & Conditions for that specific property.
7. Owner reads the document in the portal, checks agreement, and submits acceptance.
8. The system records owner, property, T&C version/document, timestamp, and acceptance, then changes the property to live/active/public.
9. If acceptance is not submitted, the property is never exposed in the public marketplace.

## Data rules
- User/Owner lifecycle is independent of Hotel lifecycle.
- Rejecting, suspending, editing, or resubmitting a hotel must not delete its owner.
- A user email identifies/reuses the owner account where appropriate; multiple hotels may link to one owner.
- T&C acceptance is property-specific and version-specific.
- Historical accepted T&C metadata must remain auditable even if the active T&C document changes later.

## Admin UI
- Approve action requires a Terms & Conditions attachment/version.
- Admin sees a clear status such as `Approved - Awaiting Owner T&C Acceptance`.
- Admin can view acceptance state and timestamp.

## Owner UI
- Notification appears after admin approval.
- T&C document is viewable in the Owner Portal without leaving the workflow.
- Owner must explicitly accept before submission.
- Successful acceptance confirms that the property is now live.

## Security
- Only admins can attach/select approval T&C documents.
- Only the linked owner can view/accept the property's pending T&C.
- Public property APIs must exclude approved-awaiting-terms properties.

## Compatibility
Existing pending/rejected/edit/resubmit workflows remain intact. Owner data must survive all property status transitions.
