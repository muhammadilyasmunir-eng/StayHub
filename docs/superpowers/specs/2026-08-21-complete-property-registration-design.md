# Complete Property Registration Design

## Goal
Expand the stable seven-step StayHub property registration wizard without changing its single-controller navigation model.

## Steps
1. Owner Account
2. Property Information
3. Facilities & Policies
4. Property Photos
5. Room Categories
6. Verification Documents
7. Review & Submit

## Property Photos
Each uploaded photo is represented as an independent entry with a required display name, category, caption/description, sort order, and optional primary flag. Categories include Main/Primary, Building/Exterior, Entrance, Reception, Lobby, Room, Restaurant, Meeting/Conference Hall, Swimming Pool, Gym/Fitness, Spa, Parking, and Other. Multiple entries are allowed for every category. Exactly one property photo is primary.

## Rooms
Each room category includes name, description, bed type, room size, room count, adult/child capacity, smoking setting, base price, currency, extra-bed details, facilities, and multiple photos. Each room photo has a required name, optional caption, primary selection, and ordering.

## Documents
Multiple documents can be added. Each includes type, license number, registration number, document number, optional issue/expiry dates and notes, plus an actual uploaded file.

## Review
Review summarizes all entered values except passwords and provides an Edit action for each section. Submit remains pending-verification oriented and uses actual upload URLs when connected to the backend upload API.

## Constraint
Navigation must use one JavaScript controller only. No injected second navigation layer, redirects with competing handlers, or inline duplicate next/previous logic.