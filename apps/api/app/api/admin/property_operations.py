from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.dependencies import get_db, require_admin
from app.models.hotel import Hotel, HotelStatus
from app.models.user import User
from app.core.security import hash_password

router=APIRouter(prefix="/admin/properties",tags=["Admin - Property Operations"])
PAYMENTS={"Cash","Credit Card","Debit Card"}; BREAKFAST={"Continental","American","Asian","Buffet","Pakistani"}
class OperationalUpdate(BaseModel):
    payment_methods:list[str]=Field(default_factory=list); parking_floors:list[str|int]=Field(default_factory=list); breakfast_options:list[str]=Field(default_factory=list); breakfast_other:str|None=None; property_highlight_floors:list[int]=Field(default_factory=list)
    def validate_values(self):
        if any(x not in PAYMENTS for x in self.payment_methods): raise ValueError("Payment methods must be Cash, Credit Card, or Debit Card")
        if any(x not in BREAKFAST for x in self.breakfast_options): raise ValueError("Unsupported breakfast option")
        if any(x not in ("Ground","Basement") and not(isinstance(x,int) and 1<=x<=200) for x in self.parking_floors): raise ValueError("Parking floors must be Ground, Basement, or 1-200")
        if any(not isinstance(x,int) or x<1 or x>200 for x in self.property_highlight_floors): raise ValueError("Property highlight floors must be between 1 and 200")
class BillingUpdate(BaseModel):
    tax_percent: Decimal = Field(ge=0, le=100)
    commission_percent: Decimal = Field(ge=0, le=100)
class PasswordReset(BaseModel): new_password:str=Field(min_length=8,max_length=128)
def _hotel(h): return {"id":h.id,"property_id":h.property_id,"name":h.name,"status":h.status,"tax_percent":h.tax_percent,"commission_percent":h.commission_percent,"payment_methods":h.payment_methods or [],"parking_floors":h.parking_floors or [],"breakfast_options":h.breakfast_options or [],"breakfast_other":h.breakfast_other,"property_highlight_floors":h.property_highlight_floors or [],"invoice_overdue":h.invoice_overdue,"duplicate_rejection":h.duplicate_rejection,"owner":{"email":h.owner.email if h.owner else None,"mobile":h.owner.phone if h.owner else None,"username":h.owner.username if h.owner else None,"password_reset_available":bool(h.owner)}}
@router.get("/status-counts")
def status_counts(db:Session=Depends(get_db),current_user:User=Depends(require_admin)):
    counts={s.value:0 for s in HotelStatus}
    for sv,count in db.query(Hotel.status,func.count(Hotel.id)).group_by(Hotel.status).all(): counts[sv.value if hasattr(sv,"value") else str(sv)]=count
    return {"active_properties":counts.get("approved",0),"pending_properties":counts.get("pending",0),"rejected_properties":counts.get("rejected",0),"invoice_overdue_properties":db.query(Hotel).filter(Hotel.invoice_overdue.is_(True)).count(),"duplicate_rejection":db.query(Hotel).filter(Hotel.duplicate_rejection.is_(True)).count(),"raw":counts}
@router.get("/{hotel_id}/operational")
def get_operational(hotel_id:int,db:Session=Depends(get_db),current_user:User=Depends(require_admin)):
    hotel=db.query(Hotel).filter(Hotel.id==hotel_id).first()
    if not hotel: raise HTTPException(404,"Property not found")
    return _hotel(hotel)
@router.put("/{hotel_id}/operational")
def update_operational(hotel_id:int,payload:OperationalUpdate,db:Session=Depends(get_db),current_user:User=Depends(require_admin)):
    try: payload.validate_values()
    except ValueError as exc: raise HTTPException(422,str(exc)) from exc
    hotel=db.query(Hotel).filter(Hotel.id==hotel_id).first()
    if not hotel: raise HTTPException(404,"Property not found")
    hotel.payment_methods=list(dict.fromkeys(payload.payment_methods)); hotel.parking_floors=list(dict.fromkeys(payload.parking_floors)); hotel.breakfast_options=list(dict.fromkeys(payload.breakfast_options)); hotel.breakfast_other=payload.breakfast_other; hotel.property_highlight_floors=sorted(set(payload.property_highlight_floors)); db.commit(); db.refresh(hotel)
    return {"message":"Property operational information updated","property":_hotel(hotel)}
@router.get("/{hotel_id}/billing")
def get_billing(hotel_id:int,db:Session=Depends(get_db),current_user:User=Depends(require_admin)):
    hotel=db.query(Hotel).filter(Hotel.id==hotel_id).first()
    if not hotel: raise HTTPException(404,"Property not found")
    return {"hotel_id":hotel.id,"property_id":hotel.property_id,"property_name":hotel.name,"tax_percent":hotel.tax_percent,"commission_percent":hotel.commission_percent,"booking_enabled":hotel.tax_percent is not None and hotel.commission_percent is not None}
@router.put("/{hotel_id}/billing")
def update_billing(hotel_id:int,payload:BillingUpdate,db:Session=Depends(get_db),current_user:User=Depends(require_admin)):
    hotel=db.query(Hotel).filter(Hotel.id==hotel_id).first()
    if not hotel: raise HTTPException(404,"Property not found")
    hotel.tax_percent=payload.tax_percent
    hotel.commission_percent=payload.commission_percent
    db.commit(); db.refresh(hotel)
    return {"message":"Property tax and commission updated","hotel_id":hotel.id,"property_id":hotel.property_id,"tax_percent":hotel.tax_percent,"commission_percent":hotel.commission_percent,"booking_enabled":True}
@router.post("/{hotel_id}/owner-reset-password")
def reset_owner_password(hotel_id:int,payload:PasswordReset,db:Session=Depends(get_db),current_user:User=Depends(require_admin)):
    hotel=db.query(Hotel).filter(Hotel.id==hotel_id).first()
    if not hotel or not hotel.owner: raise HTTPException(404,"Property owner not found")
    hotel.owner.hashed_password=hash_password(payload.new_password); db.commit(); return {"message":"Owner password reset successfully","owner_email":hotel.owner.email,"username":hotel.owner.username}
@router.delete("/{hotel_id}")
def delete_property(hotel_id:int,confirm:bool=False,db:Session=Depends(get_db),current_user:User=Depends(require_admin)):
    if not confirm: raise HTTPException(400,"Confirmation is required before deleting a property")
    hotel=db.query(Hotel).filter(Hotel.id==hotel_id).first()
    if not hotel: raise HTTPException(404,"Property not found")
    db.delete(hotel); db.commit(); return {"message":"Property deleted successfully","property_id":hotel_id}
