# Owner approval and T&C workflow

## Property lifecycle

`PENDING -> AWAITING_TERMS -> ACTIVE/LIVE`

Rejection remains `REJECTED` and never deletes the User/Owner account.

## Approval

Admin approves a property only after selecting the current active, versioned Terms & Conditions document. The property becomes `AWAITING_TERMS` and an owner notification is created. It must not appear in the public marketplace yet.

## Owner acceptance

The owner opens the notification, reads/views the attached T&C document, checks `I have read and agree to the Terms & Conditions`, and submits. The system records property, owner, T&C version/file, timestamp, IP and user agent, then changes the property to `ACTIVE`/`LIVE`.

## Owner persistence

A rejected property changes property status only. The User/Owner remains persisted. Multiple properties may reference the same owner account.

## T&C versioning

T&C documents are centrally managed and versioned. Each property acceptance references the exact document version accepted, preserving an audit trail even after a newer version becomes active.
