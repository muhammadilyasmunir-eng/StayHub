from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user, require_admin
from app.models.hotel import Hotel, HotelStatus
from app.models.notification import Notification
from app.models.terms_acceptance import TermsDocument, HotelTermsAcceptance
from app.models.user import User

router = APIRouter(prefix="/admin/terms", tags=["Admin - Terms"])
DOC_TYPES = {"terms": "Terms & Conditions", "accommodation": "Accommodation Agreement", "contract": "Contract"}

def _term_payload(doc: TermsDocument):
    return {"id": doc.id, "version": doc.version, "document_type": doc.document_type, "document_name": DOC_TYPES.get(doc.document_type, "Agreement Form" if doc.document_type == "agreement_form" else doc.document_type), "terms_text": doc.description or "", "description": doc.description or "", "active": doc.active, "uploaded_at": doc.uploaded_at}

def _assigned_documents(hotel_id: int, owner_id: int, db: Session):
    note = db.query(Notification).filter(Notification.hotel_id == hotel_id, Notification.user_id == owner_id, Notification.type == "terms_required").order_by(Notification.created_at.desc()).first()
    ids = []
    if note and "[terms_ids:" in note.message:
        try:
            raw = note.message.split("[terms_ids:", 1)[1].split("]", 1)[0]
            ids = [int(x) for x in raw.split(",") if x.strip()]
        except (ValueError, IndexError): ids = []
    if ids:
        docs = db.query(TermsDocument).filter(TermsDocument.id.in_(ids)).all(); by_type = {d.document_type: d for d in docs}
        if all(t in by_type for t in DOC_TYPES): return by_type
    docs = db.query(TermsDocument).filter(TermsDocument.active.is_(True)).order_by(TermsDocument.uploaded_at.desc()).all()
    return {t: next((d for d in docs if d.document_type == t and (d.description or "").strip()), None) for t in DOC_TYPES}

@router.get("")
def list_terms(db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    return [_term_payload(d) for d in db.query(TermsDocument).order_by(TermsDocument.uploaded_at.desc()).all()]

@router.post("/upload", status_code=status.HTTP_201_CREATED)
def save_terms(version: str = Form(...), terms_text: str = Form(...), document_type: str = Form("terms"), db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    version = version.strip(); text = terms_text.strip(); document_type = document_type.strip().lower(); allowed = {**DOC_TYPES, "agreement_form": "Agreement Form"}
    if document_type not in allowed: raise HTTPException(400, "Invalid approval document type")
    if not version: raise HTTPException(400, "Version is required")
    if not text: raise HTTPException(400, f"Enter {allowed[document_type]} text")
    doc = db.query(TermsDocument).filter(TermsDocument.version == version, TermsDocument.document_type == document_type).first()
    if doc:
        doc.description = text; doc.file_name = f"{allowed[document_type]} text"; doc.file_url = ""; doc.uploaded_by = current_user.id; doc.active = True
        db.query(TermsDocument).filter(TermsDocument.document_type == document_type, TermsDocument.id != doc.id).update({TermsDocument.active: False})
    else:
        other = db.query(TermsDocument).filter(TermsDocument.version == version, TermsDocument.document_type != document_type).first()
        if other: raise HTTPException(400, f"Version {version} is already used by {other.document_type}. Use a different version for this document.")
        db.query(TermsDocument).filter(TermsDocument.document_type == document_type).update({TermsDocument.active: False})
        doc = TermsDocument(version=version, document_type=document_type, file_name=f"{allowed[document_type]} text", file_url="", description=text, uploaded_by=current_user.id, active=True); db.add(doc)
    db.commit(); db.refresh(doc); return _term_payload(doc)

@router.post("/{terms_id}/activate")
def activate_terms(terms_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    doc = db.query(TermsDocument).filter(TermsDocument.id == terms_id).first()
    if not doc: raise HTTPException(404, "Approval document version not found")
    if not (doc.description or "").strip(): raise HTTPException(400, "This document has no text")
    db.query(TermsDocument).filter(TermsDocument.document_type == doc.document_type, TermsDocument.id != doc.id).update({TermsDocument.active: False}); doc.active = True; db.commit(); return {"message": "Document version activated", **_term_payload(doc)}

@router.post("/property/{hotel_id}/approve")
def approve_with_terms(hotel_id: int, terms_id: int | None = Form(None), db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    hotel = db.query(Hotel).filter(Hotel.id == hotel_id).first()
    if not hotel: raise HTTPException(404, "Property not found")
    if not hotel.owner_id: raise HTTPException(400, "Property has no owner")
    active_docs = db.query(TermsDocument).filter(TermsDocument.active.is_(True)).all(); by_type = {d.document_type: d for d in active_docs if (d.description or "").strip()}
    if terms_id:
        old = db.query(TermsDocument).filter(TermsDocument.id == terms_id).first()
        if old and old.document_type == "terms" and (old.description or "").strip(): by_type["terms"] = old
    missing = [DOC_TYPES[t] for t in DOC_TYPES if t not in by_type]
    if missing: raise HTTPException(400, "Save active text for: " + ", ".join(missing))
    agreement_form = db.query(TermsDocument).filter(TermsDocument.document_type == "agreement_form", TermsDocument.active.is_(True)).order_by(TermsDocument.uploaded_at.desc()).first()
    if not agreement_form or not (agreement_form.description or "").strip(): raise HTTPException(400, "Save active text for: Agreement Form")
    hotel.status = HotelStatus.AWAITING_TERMS; hotel.rejection_reason = None; hotel.approved_at = None; hotel.approved_by = current_user.id; hotel.owner_cnic_front_url = None; hotel.owner_cnic_back_url = None; hotel.signed_agreement_url = None; hotel.agreement_submitted_at = None; hotel.owner_documents_submitted = False
    db.query(HotelTermsAcceptance).filter(HotelTermsAcceptance.hotel_id == hotel.id).delete(synchronize_session=False)
    db.query(Notification).filter(Notification.hotel_id == hotel.id, Notification.user_id == hotel.owner_id, Notification.type == "terms_required").delete(synchronize_session=False)
    ids = [str(by_type[t].id) for t in DOC_TYPES]
    db.add(Notification(user_id=hotel.owner_id, hotel_id=hotel.id, title="Approval Documents Required", message="Your property has been approved for the owner verification stage. Please review and accept the Terms & Conditions, Accommodation Agreement and Contract, then complete the CNIC/Passport and signed Agreement Form submission. The property will go to Admin for final review and will not be live before that. [terms_ids:" + ",".join(ids) + "]", type="terms_required", read=False))
    db.commit(); return {"message": "Property approved for owner document stage; awaiting final admin review", "status": hotel.status.value if hasattr(hotel.status, "value") else str(hotel.status), "hotel_id": hotel.id, "document_ids": {t: by_type[t].id for t in DOC_TYPES}, "agreement_form_id": agreement_form.id}

@router.get("/property/{hotel_id}")
def get_property_terms(hotel_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    hotel = db.query(Hotel).filter(Hotel.id == hotel_id, Hotel.owner_id == current_user.id).first()
    if not hotel: raise HTTPException(404, "Property not found")
    assigned = _assigned_documents(hotel.id, current_user.id, db); accepted_ids = {x.terms_document_id for x in db.query(HotelTermsAcceptance).filter(HotelTermsAcceptance.hotel_id == hotel.id, HotelTermsAcceptance.owner_id == current_user.id).all()}; docs = [_term_payload(assigned[t]) | {"accepted": bool(assigned[t] and assigned[t].id in accepted_ids)} for t in DOC_TYPES if assigned.get(t)]
    return {"property_id": hotel.id, "status": hotel.status, "all_accepted": len(docs) == 3 and all(x["accepted"] for x in docs), "documents": docs}

@router.post("/property/{hotel_id}/accept")
def accept_property_terms(hotel_id: int, terms_id: int = Form(...), request: Request = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    hotel = db.query(Hotel).filter(Hotel.id == hotel_id, Hotel.owner_id == current_user.id).first()
    if not hotel: raise HTTPException(404, "Property not found")
    assigned = _assigned_documents(hotel.id, current_user.id, db)
    # The terms notification is the source of truth for the owner approval stage.
    # This also tolerates an older PENDING/INACTIVE status left by the previous workflow,
    # while still requiring an actually assigned approval document before acceptance.
    if hotel.status not in (HotelStatus.AWAITING_TERMS, HotelStatus.INACTIVE, HotelStatus.APPROVED, HotelStatus.PENDING):
        raise HTTPException(400, "This property is not awaiting approval documents")
    assigned_doc = next((d for d in assigned.values() if d and d.id == terms_id), None)
    if not assigned_doc: raise HTTPException(400, "This document is not assigned to this property")
    if hotel.status == HotelStatus.INACTIVE: hotel.status = HotelStatus.AWAITING_TERMS
    existing = db.query(HotelTermsAcceptance).filter(HotelTermsAcceptance.hotel_id == hotel.id, HotelTermsAcceptance.owner_id == current_user.id, HotelTermsAcceptance.terms_document_id == terms_id).first()
    if not existing:
        db.add(HotelTermsAcceptance(hotel_id=hotel.id, terms_document_id=terms_id, owner_id=current_user.id, ip_address=request.client.host if request and request.client else None, user_agent=request.headers.get("user-agent") if request else None)); db.flush()
    accepted_ids = {x.terms_document_id for x in db.query(HotelTermsAcceptance).filter(HotelTermsAcceptance.hotel_id == hotel.id, HotelTermsAcceptance.owner_id == current_user.id).all()}; required_ids = {d.id for d in assigned.values() if d}; all_accepted = required_ids.issubset(accepted_ids) and len(required_ids) == 3
    db.commit(); return {"message": "Document accepted. You can continue with the remaining approval documents." if not all_accepted else "All three documents accepted. Complete the verification upload and submit for final Admin review.", "status": hotel.status.value if hasattr(hotel.status, "value") else str(hotel.status), "all_accepted": all_accepted, "accepted_document_type": assigned_doc.document_type}

@router.get("/notifications")
def owner_notifications(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    rows = db.query(Notification).filter(Notification.user_id == current_user.id).order_by(Notification.created_at.desc()).all()
    return [{"id": n.id, "hotel_id": n.hotel_id, "title": n.title, "message": n.message.split(" [terms_ids:", 1)[0].split(" [terms_id:", 1)[0], "type": n.type, "read": n.read, "created_at": n.created_at} for n in rows]
