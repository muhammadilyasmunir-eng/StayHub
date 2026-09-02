from datetime import datetime
from fastapi import APIRouter, Depends, Form, HTTPException, Request
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user, require_admin
from app.models.hotel import Hotel, HotelStatus
from app.models.hotel_document import HotelDocument
from app.models.notification import Notification
from app.models.terms_acceptance import TermsDocument, HotelTermsAcceptance
from app.models.user import User

router = APIRouter(prefix="/admin/verification", tags=["Approval Verification"])
REQUIRED = ("terms", "accommodation", "contract")

def docs_for(hotel_id, owner_id, db):
    note = db.query(Notification).filter(Notification.hotel_id == hotel_id, Notification.user_id == owner_id, Notification.type == "terms_required").order_by(Notification.created_at.desc()).first()
    ids=[]
    if note and "[terms_ids:" in note.message:
        try: ids=[int(x) for x in note.message.split("[terms_ids:",1)[1].split("]",1)[0].split(",") if x.strip()]
        except ValueError: ids=[]
    if ids:
        rows=db.query(TermsDocument).filter(TermsDocument.id.in_(ids)).all(); by={x.document_type:x for x in rows}
        if all(x in by for x in REQUIRED): return by
    rows=db.query(TermsDocument).filter(TermsDocument.active == True).all()
    return {x: next((d for d in rows if d.document_type == x and (d.description or "").strip()), None) for x in REQUIRED}

def payload(d):
    return {"id":d.id,"version":d.version,"document_type":d.document_type,"document_name":{"terms":"Terms & Conditions","accommodation":"Accommodation Agreement","contract":"Contract","agreement_form":"Agreement Form"}.get(d.document_type,d.document_type),"terms_text":d.description or "","active":d.active}

@router.get("/property/{hotel_id}")
def owner_verification(hotel_id:int, db:Session=Depends(get_db), current_user:User=Depends(get_current_user)):
    h=db.query(Hotel).filter(Hotel.id==hotel_id,Hotel.owner_id==current_user.id).first()
    if not h: raise HTTPException(404,"Property not found")
    ds=docs_for(h.id,current_user.id,db)
    form=db.query(TermsDocument).filter(TermsDocument.document_type=="agreement_form",TermsDocument.active==True).order_by(TermsDocument.uploaded_at.desc()).first()
    accepted={x.terms_document_id for x in db.query(HotelTermsAcceptance).filter(HotelTermsAcceptance.hotel_id==h.id,HotelTermsAcceptance.owner_id==current_user.id).all()}
    docs=[payload(ds[x])|{"accepted":ds[x].id in accepted} for x in REQUIRED if ds.get(x)]
    return {"property_id":h.id,"status":h.status,"documents":docs,"agreement_form":payload(form) if form else None,"cnic_front_uploaded":bool(h.owner_cnic_front_url),"cnic_back_uploaded":bool(h.owner_cnic_back_url),"signed_agreement_uploaded":bool(h.signed_agreement_url),"submitted":h.owner_documents_submitted}

@router.post("/property/{hotel_id}/accept")
def owner_accept(hotel_id:int, terms_id:int=Form(...), request:Request=None, db:Session=Depends(get_db), current_user:User=Depends(get_current_user)):
    h=db.query(Hotel).filter(Hotel.id==hotel_id,Hotel.owner_id==current_user.id).first()
    if not h: raise HTTPException(404,"Property not found")
    ds=docs_for(h.id,current_user.id,db)
    # Accept only a document assigned by the Admin approval notification.
    # Keep compatibility with legacy properties that can still be PENDING/INACTIVE.
    if h.status not in (HotelStatus.INACTIVE,HotelStatus.AWAITING_TERMS,HotelStatus.APPROVED,HotelStatus.PENDING):
        raise HTTPException(400,"This property is not awaiting approval documents")
    d=next((x for x in ds.values() if x and x.id==terms_id),None)
    if not d or d.document_type not in REQUIRED: raise HTTPException(400,"This approval document is not assigned to this property")
    exists=db.query(HotelTermsAcceptance).filter(HotelTermsAcceptance.hotel_id==h.id,HotelTermsAcceptance.owner_id==current_user.id,HotelTermsAcceptance.terms_document_id==terms_id).first()
    if not exists:
        db.add(HotelTermsAcceptance(hotel_id=h.id,terms_document_id=terms_id,owner_id=current_user.id,ip_address=request.client.host if request and request.client else None,user_agent=request.headers.get("user-agent") if request else None))
        db.commit()
    accepted={x.terms_document_id for x in db.query(HotelTermsAcceptance).filter(HotelTermsAcceptance.hotel_id==h.id,HotelTermsAcceptance.owner_id==current_user.id).all()}
    required={ds[x].id for x in REQUIRED if ds.get(x)}
    return {"message":"Document accepted","all_accepted":len(required)==3 and required.issubset(accepted),"status":h.status}

@router.post("/property/{hotel_id}/submit")
def owner_submit(hotel_id:int, cnic_front_url:str=Form(...), cnic_back_url:str=Form(...), signed_agreement_url:str=Form(...), db:Session=Depends(get_db), current_user:User=Depends(get_current_user)):
    h=db.query(Hotel).filter(Hotel.id==hotel_id,Hotel.owner_id==current_user.id).first()
    if not h: raise HTTPException(404,"Property not found")
    ds=docs_for(h.id,current_user.id,db); accepted={x.terms_document_id for x in db.query(HotelTermsAcceptance).filter(HotelTermsAcceptance.hotel_id==h.id,HotelTermsAcceptance.owner_id==current_user.id).all()}; required={ds[x].id for x in REQUIRED if ds.get(x)}
    if len(required)!=3 or not required.issubset(accepted): raise HTTPException(400,"Accept all three approval documents first")
    for value,label in ((cnic_front_url,"CNIC/Passport Front"),(cnic_back_url,"CNIC/Passport Back"),(signed_agreement_url,"Signed Agreement")):
        if not value.strip(): raise HTTPException(400,f"{label} is required")
    h.owner_cnic_front_url=cnic_front_url.strip(); h.owner_cnic_back_url=cnic_back_url.strip(); h.signed_agreement_url=signed_agreement_url.strip(); h.agreement_submitted_at=datetime.utcnow(); h.owner_documents_submitted=True
    # Owner submission always returns the property to the Admin Pending queue.
    # It stays non-live until Admin performs the final Go For Live action.
    h.status = HotelStatus.PENDING
    for typ,url in (("owner_cnic_front",h.owner_cnic_front_url),("owner_cnic_back",h.owner_cnic_back_url),("signed_agreement",h.signed_agreement_url)):
        db.add(HotelDocument(hotel_id=h.id,document_type=typ,document_url=url,status="submitted"))
    db.query(Notification).filter(Notification.hotel_id==h.id,Notification.user_id==current_user.id,Notification.type=="terms_required",Notification.read==False).update({Notification.read:True})
    admins=db.query(User).filter(User.role=="admin").all()
    for admin in admins: db.add(Notification(user_id=admin.id,hotel_id=h.id,title="Property Ready for Final Review",message=f"{h.name} has submitted CNIC/Passport and signed Agreement Form. Review and use Go For Live.",type="admin_review_required",read=False))
    db.commit(); return {"message":"Submitted for final admin review","status":"pending","admin_review_required":True}

@router.get("/queue")
def queue(db:Session=Depends(get_db), current_user:User=Depends(require_admin)):
    rows=db.query(Hotel).filter(Hotel.owner_documents_submitted==True,Hotel.status!=HotelStatus.APPROVED).order_by(Hotel.updated_at.desc()).all()
    return [{"id":h.id,"name":h.name,"property_id":h.property_id,"owner_id":h.owner_id,"status":h.status,"cnic_front_url":h.owner_cnic_front_url,"cnic_back_url":h.owner_cnic_back_url,"signed_agreement_url":h.signed_agreement_url,"agreement_submitted_at":h.agreement_submitted_at} for h in rows]

@router.post("/property/{hotel_id}/go-live")
def go_live(hotel_id:int, db:Session=Depends(get_db), current_user:User=Depends(require_admin)):
    h=db.query(Hotel).filter(Hotel.id==hotel_id).first()
    if not h: raise HTTPException(404,"Property not found")
    if not h.owner_documents_submitted or not h.owner_cnic_front_url or not h.owner_cnic_back_url or not h.signed_agreement_url: raise HTTPException(400,"Owner verification documents are incomplete")
    h.status=HotelStatus.APPROVED; h.approved_at=datetime.utcnow(); h.approved_by=current_user.id
    db.query(Notification).filter(Notification.hotel_id==h.id,Notification.type=="admin_review_required",Notification.read==False).update({Notification.read:True})
    if h.owner_id: db.add(Notification(user_id=h.owner_id,hotel_id=h.id,title="Property Is Live",message="Your property has passed final admin review and is now live on StayHub.",type="property_live",read=False))
    db.commit(); return {"message":"Property is now live","status":"approved"}
