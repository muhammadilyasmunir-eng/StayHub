# Final Property Review and Live Properties Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the complete admin final-review workflow and Live Properties management area without breaking the existing stable Pending Properties flow.

**Architecture:** Keep `serialize_hotel()` in `apps/api/app/api/admin/hotels.py` as the complete property-profile source. Keep owner document submission and Go For Live validation in `apps/api/app/api/admin/verification.py`. Extend the admin hotel lifecycle API for send-back, close, delete and live-list operations, then extend `admin-property-operations.js` without replacing its protected pending-list rendering path.

**Tech Stack:** FastAPI, SQLAlchemy, PostgreSQL, vanilla JavaScript, existing StayHub static admin UI.

**Spec:** `docs/superpowers/specs/2026-08-28-final-property-review-live-properties-design.md`

## Global Constraints

- Preserve the current stable `/admin/hotels/pending` rendering behavior.
- `PENDING` with `owner_documents_submitted=true` is displayed as `Ready for Final Review`.
- `AWAITING_TERMS` remains the owner document acceptance/submission stage.
- Only `APPROVED` properties are eligible for the public marketplace and Live Properties.
- Go For Live remains blocked until CNIC/Passport Front, CNIC/Passport Back and Signed Agreement are present.
- Send Back requires a non-empty reason and must keep the property non-public.
- Close must preserve the property record while hiding it from the marketplace.
- Delete must require explicit browser confirmation and use existing relationship/cascade behavior.
- API errors must leave the currently displayed profile/list intact and show the backend error.

---

### Task 1: Add lifecycle API coverage for final review and live property management

**Files:**
- Modify: `apps/api/app/api/admin/hotels.py`
- Modify: `apps/api/app/api/admin/verification.py`
- Test: `apps/api/tests/test_property_lifecycle.py`

**Interfaces:**
- Consumes: `Hotel`, `HotelStatus`, `Notification`, `serialize_hotel(hotel)`.
- Produces: `POST /admin/hotels/{hotel_id}/send-back`, `POST /admin/hotels/{hotel_id}/close`, `DELETE /admin/hotels/{hotel_id}`, `GET /admin/hotels/live`, and existing `POST /admin/verification/property/{hotel_id}/go-live`.

- [ ] **Step 1: Write failing lifecycle tests**

```python
def test_live_endpoint_returns_only_approved(client, admin_token, approved_hotel, pending_hotel):
    response = client.get('/admin/hotels/live', headers=admin_token)
    assert response.status_code == 200
    assert [row['id'] for row in response.json()] == [approved_hotel.id]


def test_send_back_requires_reason(client, admin_token, final_review_hotel):
    response = client.post(f'/admin/hotels/{final_review_hotel.id}/send-back', headers=admin_token, json={})
    assert response.status_code == 400


def test_close_preserves_record_and_marks_suspended(client, admin_token, approved_hotel, db):
    response = client.post(f'/admin/hotels/{approved_hotel.id}/close', headers=admin_token)
    assert response.status_code == 200
    db.refresh(approved_hotel)
    assert approved_hotel.status.value == 'suspended'
```

- [ ] **Step 2: Run tests to verify failure**

Run:

```powershell
cd F:\Projects\StayHub\apps\api
pytest tests/test_property_lifecycle.py -v
```

Expected: lifecycle routes are missing or assertions fail before implementation.

- [ ] **Step 3: Implement minimal lifecycle routes**

Add `Notification` import and implement:

```python
@router.get('/live')
def get_live_hotels(...):
    hotels = db.query(Hotel).filter(Hotel.status == HotelStatus.APPROVED).order_by(Hotel.created_at.desc()).all()
    return [serialize_hotel(h) for h in hotels]

@router.post('/{hotel_id}/send-back')
def send_back_hotel(hotel_id: int, reason: str, ...):
    if not reason.strip():
        raise HTTPException(400, 'Rejection reason is required')
    hotel.status = HotelStatus.REJECTED
    hotel.rejection_reason = reason.strip()
    hotel.approved_at = None
    hotel.approved_by = None
    db.add(Notification(..., type='property_correction_required', ...))
    db.commit()
    return {'message': 'Property sent back to owner', 'hotel': serialize_hotel(hotel)}

@router.post('/{hotel_id}/close')
def close_hotel(hotel_id: int, ...):
    hotel.status = HotelStatus.SUSPENDED
    db.commit()
    return {'message': 'Property closed successfully', 'hotel': serialize_hotel(hotel)}

@router.delete('/{hotel_id}')
def delete_hotel(hotel_id: int, ...):
    db.delete(hotel)
    db.commit()
    return {'message': 'Property deleted successfully'}
```

Use the existing owner notification fields and rejection flow conventions. Do not alter `/pending` filtering.

- [ ] **Step 4: Run lifecycle tests**

Run:

```powershell
cd F:\Projects\StayHub\apps\api
pytest tests/test_property_lifecycle.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```powershell
cd F:\Projects\StayHub
git add apps/api/app/api/admin/hotels.py apps/api/app/api/admin/verification.py apps/api/tests/test_property_lifecycle.py
git commit -m "feat: add property final review lifecycle api"
git push origin main
```

### Task 2: Make final-review state explicit in complete admin serialization

**Files:**
- Modify: `apps/api/app/api/admin/hotels.py`
- Test: `apps/api/tests/test_property_lifecycle.py`

**Interfaces:**
- Consumes: `Hotel.status`, `Hotel.owner_documents_submitted`.
- Produces: serialized `review_state` with values `ready_for_final_review`, `awaiting_owner_documents`, or `live`.

- [ ] **Step 1: Write failing serializer test**

```python
def test_pending_owner_submission_serializes_as_ready_for_final_review(final_review_hotel):
    payload = serialize_hotel(final_review_hotel)
    assert payload['review_state'] == 'ready_for_final_review'
```

- [ ] **Step 2: Run test to verify failure**

```powershell
cd F:\Projects\StayHub\apps\api
pytest tests/test_property_lifecycle.py::test_pending_owner_submission_serializes_as_ready_for_final_review -v
```

Expected: FAIL because `review_state` is absent.

- [ ] **Step 3: Implement presentation state in serializer**

```python
def review_state(hotel: Hotel) -> str:
    if hotel.status == HotelStatus.APPROVED:
        return 'live'
    if hotel.status == HotelStatus.PENDING and hotel.owner_documents_submitted:
        return 'ready_for_final_review'
    if hotel.status == HotelStatus.AWAITING_TERMS:
        return 'awaiting_owner_documents'
    return str(hotel.status.value if hasattr(hotel.status, 'value') else hotel.status)
```

Include `owner_documents_submitted`, `agreement_submitted_at`, `owner_cnic_front_url`, `owner_cnic_back_url`, `signed_agreement_url`, and `review_state` in `serialize_hotel()`.

- [ ] **Step 4: Run serializer tests**

```powershell
cd F:\Projects\StayHub\apps\api
pytest tests/test_property_lifecycle.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```powershell
cd F:\Projects\StayHub
git add apps/api/app/api/admin/hotels.py apps/api/tests/test_property_lifecycle.py
git commit -m "feat: expose final review state in admin property profile"
git push origin main
```

### Task 3: Add complete property profile and Pending final-review UI

**Files:**
- Modify: `apps/api/app/static/admin-property-operations.js`
- Test: browser smoke test through Admin UI

**Interfaces:**
- Consumes: `GET /admin/hotels/{hotel_id}` complete profile and serialized `review_state`.
- Produces: `window.stayhubOpenProperty(id, mode)`, a reusable property-detail section, `Go For Live`, and `Send Back to Owner` actions.

- [ ] **Step 1: Add a protected Pending row renderer test fixture/check**

Use a fixture response containing one `AWAITING_TERMS` property and one `PENDING + owner_documents_submitted=true` property. Verify that rendering labels the second row `Ready for Final Review` and does not replace `pendingHotels` with generic status filtering.

- [ ] **Step 2: Confirm current Pending path before editing**

Run in PowerShell:

```powershell
cd F:\Projects\StayHub
Select-String -Path .\apps\api\app\static\admin-property-operations.js -Pattern "pendingHotels|stayhubLoadPending|renderRows\('pending'" -Context 0,2
```

Expected: dedicated `pendingHotels` cache and `/admin/hotels/pending` loader are present.

- [ ] **Step 3: Implement reusable complete-profile renderer**

Create focused helpers in the existing file:

```javascript
function propertyStatusLabel(h) {
  if (h.review_state === 'ready_for_final_review') return 'Ready for Final Review';
  if (h.review_state === 'live') return 'Live';
  return String(h.status || '—').replaceAll('_', ' ');
}

async function openProperty(id, mode='review') {
  const hotel = await req('/admin/hotels/' + id);
  renderPropertyDetail(hotel, mode);
}
```

Render sections for property details, owner details, rooms/rates, facilities, policies, photos, registration documents, CNIC/Passport Front, CNIC/Passport Back and Signed Agreement. Every available document URL must render a safe `View Document` link using `target="_blank"` and `rel="noopener"`.

Pending rows must become clickable and preserve the existing stable loader. Final actions appear only when `review_state === 'ready_for_final_review'`.

- [ ] **Step 4: Implement final review actions**

Use:

```javascript
async function goLive(id) {
  const result = await req('/admin/verification/property/' + id + '/go-live', {method:'POST'});
  alert(result.message || 'Property is now live');
  await window.stayhubLoadProperties();
  show('property-status-live', document.querySelector('[data-stayhub-nav="property-status-live"]'));
}

async function sendBack(id) {
  const reason = prompt('Enter the reason for sending this property back to the owner:');
  if (!reason || !reason.trim()) return alert('Rejection reason is required.');
  const result = await req('/admin/hotels/' + id + '/send-back', {
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({reason: reason.trim()})
  });
  alert(result.message || 'Property sent back to owner');
  await window.stayhubLoadProperties();
}
```

Do not clear the current detail view until the action succeeds.

- [ ] **Step 5: Browser smoke test**

Open the admin panel, then verify:

1. Pending property remains visible after page load and refresh.
2. Final-review-ready property shows `Ready for Final Review`.
3. Clicking the property opens the complete profile.
4. CNIC Front, CNIC Back and Signed Agreement links are visible when submitted.
5. Go For Live succeeds only when verification documents are complete.
6. Send Back without a reason is blocked.

- [ ] **Step 6: Commit**

```powershell
cd F:\Projects\StayHub
git add apps/api/app/static/admin-property-operations.js
git commit -m "feat: add admin final property review ui"
git push origin main
```

### Task 4: Add dedicated Live Properties dashboard and management UI

**Files:**
- Modify: `apps/api/app/static/admin-property-operations.js`
- Test: browser smoke test through Admin UI

**Interfaces:**
- Consumes: `GET /admin/hotels/live`, `POST /admin/hotels/{id}/close`, `DELETE /admin/hotels/{id}`, and existing admin update route.
- Produces: `Live Properties` card/nav, live list, profile actions for Edit, Close and Delete.

- [ ] **Step 1: Add Live Properties section and dashboard card**

Add `property-status-live` to navigation and dashboard with its own `dashLive` count. Keep existing Active Properties behavior untouched to avoid changing stable existing semantics.

- [ ] **Step 2: Implement live loader**

```javascript
let liveHotels = [];

window.stayhubLoadLive = async () => {
  const rows = await req('/admin/hotels/live');
  liveHotels = Array.isArray(rows) ? rows : [];
  renderLiveRows(liveHotels);
  if ($('dashLive')) $('dashLive').textContent = liveHotels.length;
};
```

Only call this dedicated loader for the Live Properties section.

- [ ] **Step 3: Add live profile actions**

Add buttons:

```javascript
async function closeProperty(id) {
  if (!confirm('Close this property? It will be hidden from the public marketplace but kept in StayHub.')) return;
  await req('/admin/hotels/' + id + '/close', {method:'POST'});
  await window.stayhubLoadProperties();
  await window.stayhubLoadLive();
}

async function deleteProperty(id) {
  if (!confirm('Delete this property permanently? This action cannot be undone.')) return;
  await req('/admin/hotels/' + id, {method:'DELETE'});
  await window.stayhubLoadProperties();
  await window.stayhubLoadLive();
}
```

Edit uses the existing `PUT /admin/hotels/{hotel_id}` contract and preloads the same complete property data into the existing editable surface or a focused admin edit form.

- [ ] **Step 4: Browser smoke test**

Verify:

1. Only approved properties appear in Live Properties.
2. Go For Live removes the property from final-review Pending and makes it appear in Live Properties.
3. Opening a live property shows the complete profile.
4. Close removes it from Live Properties/public eligibility but does not delete it.
5. Delete requires confirmation and removes the property after confirmation.
6. Existing Pending list still remains visible after refresh.

- [ ] **Step 5: Commit**

```powershell
cd F:\Projects\StayHub
git add apps/api/app/static/admin-property-operations.js
git commit -m "feat: add live properties admin management"
git push origin main
```

### Task 5: Full regression verification and deployment handoff

**Files:**
- Verify: `apps/api/app/api/admin/hotels.py`
- Verify: `apps/api/app/api/admin/verification.py`
- Verify: `apps/api/app/static/admin-property-operations.js`

**Interfaces:**
- Verifies all lifecycle and UI interfaces from Tasks 1-4.

- [ ] **Step 1: Run focused backend tests**

```powershell
cd F:\Projects\StayHub\apps\api
pytest tests/test_property_lifecycle.py -v
```

Expected: PASS.

- [ ] **Step 2: Run import/syntax checks**

```powershell
cd F:\Projects\StayHub
python -m compileall .\apps\api\app
node --check .\apps\api\app\static\admin-property-operations.js
```

Expected: no syntax errors.

- [ ] **Step 3: Sync local repository and restart/open the web app**

```powershell
cd F:\Projects\StayHub
git pull origin main
```

Then use the project's existing local start command. After the server is running, open the local admin URL already used by the StayHub project.

- [ ] **Step 4: Verify through the web UI**

Test the exact lifecycle:

```text
Owner submits documents
→ Pending Properties remains populated
→ Ready for Final Review
→ Complete Profile
→ Go For Live
→ Live Properties
→ Close
```

Then separately test:

```text
Ready for Final Review
→ Send Back with required reason
→ Owner receives correction notification
→ Property remains non-public
```

- [ ] **Step 5: Final commit and push**

```powershell
cd F:\Projects\StayHub
git status
git add apps/api/app/api/admin/hotels.py apps/api/app/api/admin/verification.py apps/api/app/static/admin-property-operations.js apps/api/tests/test_property_lifecycle.py docs/superpowers/plans/2026-08-28-final-property-review-live-properties.md
git commit -m "feat: complete final property review and live management"
git push origin main
```
