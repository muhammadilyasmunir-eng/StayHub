from datetime import datetime, timezone

from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_db, require_admin
from app.models.hotel import Hotel, HotelStatus
from app.models.hotel_document import HotelDocument
from app.models.hotel_facility import HotelFacility
from app.models.hotel_photo import HotelPhoto
from app.models.hotel_policy import HotelPolicy
from app.models.notification import Notification
from app.models.room_type import RoomType
from app.models.room_type_facility import RoomTypeFacility
from app.models.room_type_photo import RoomTypePhoto
from app.models.user import User
from app.schemas.hotel import AdminHotelUpdate

router = APIRouter(prefix="/admin/hotels", tags=["Admin - Hotels"])

def _status_value(value): return value.value if hasattr(value,"value") else str(value)
def review_state(hotel: Hotel) -> str:
    if hotel.status == HotelStatus.APPROVED: return "live"
    if hotel.status == HotelStatus.PENDING and hotel.owner_documents_submitted: return "ready_for_final_review"
    if hotel.status == HotelStatus.AWAITING_TERMS: return "awaiting_owner_documents"
    return _status_value(hotel.status)
def serialize_hotel(hotel: Hotel):
    return {"id":hotel.id,"property_id":hotel.property_id,"owner_id":hotel.owner_id,"name":hotel.name,"slug":hotel.slug,"property_type":hotel.property_type,"description":hotel.description,"star_rating":hotel.star_rating,"email":hotel.email,"phone":hotel.phone,"alternate_phone":hotel.alternate_phone,"website":hotel.website,"country":hotel.country,"city":hotel.city,"address":hotel.address,"postal_code":hotel.postal_code,"latitude":hotel.latitude,"longitude":hotel.longitude,"total_rooms":hotel.total_rooms,"check_in_time":hotel.check_in_time,"check_out_time":hotel.check_out_time,"timezone":hotel.timezone,"currency":hotel.currency,"tax_percent":float(hotel.tax_percent) if hotel.tax_percent is not None else None,"commission_percent":float(hotel.commission_percent) if hotel.commission_percent is not None else None,"booking_enabled":hotel.tax_percent is not None and hotel.commission_percent is not None,"status":review_state(hotel),"rejection_reason":hotel.rejection_reason,"approved_at":hotel.approved_at,"created_at":hotel.created_at,"owner_documents_submitted":bool(hotel.owner_documents_submitted),"agreement_submitted_at":hotel.agreement_submitted_at,"owner_cnic_front_url":hotel.owner_cnic_front_url,"owner_cnic_back_url":hotel.owner_cnic_back_url,"signed_agreement_url":hotel.signed_agreement_url,"review_state":review_state(hotel),"payment_methods":hotel.payment_methods or [],"parking_floors":hotel.parking_floors or [],"breakfast_options":hotel.breakfast_options or [],"breakfast_other":hotel.breakfast_other,"property_highlight_floors":hotel.property_highlight_floors or [],"owner":{"id":hotel.owner.id if hotel.owner else None,"name":hotel.owner.full_name if hotel.owner else None,"email":hotel.owner.email if hotel.owner else None,"phone":hotel.owner.phone if hotel.owner else None,"username":hotel.owner.username if hotel.owner else None},"facilities":[{"id":x.id,"name":x.name,"available":x.available} for x in hotel.facilities],"policy":{"cancellation_policy":hotel.policy.cancellation_policy if hotel.policy else None,"child_policy":hotel.policy.child_policy if hotel.policy else None,"pet_policy":hotel.policy.pet_policy if hotel.policy else None,"smoking_policy":hotel.policy.smoking_policy if hotel.policy else None,"payment_methods":hotel.policy.payment_methods if hotel.policy else None,"extra_bed_policy":hotel.policy.extra_bed_policy if hotel.policy else None,"age_restriction":hotel.policy.age_restriction if hotel.policy else None,"quiet_hours":hotel.policy.quiet_hours if hotel.policy else None,"house_rules":hotel.policy.house_rules if hotel.policy else None},"photos":[{"id":x.id,"url":x.photo_url,"caption":x.caption,"category":x.category,"is_primary":x.is_primary,"sort_order":x.sort_order} for x in hotel.photos],"documents":[{"id":x.id,"type":x.document_type,"license_number":x.license_number,"registration_number":x.registration_number,"document_number":x.document_number,"url":x.document_url,"status":x.status,"admin_notes":x.admin_notes} for x in hotel.documents],"room_types":[{"id":x.id,"name":x.name,"description":x.description,"number_of_rooms":x.number_of_rooms,"max_adults":x.max_adults,"max_children":x.max_children,"bed_type":x.bed_type,"room_size":x.room_size,"base_price":float(x.base_price),"discount_percent":float(x.discount_percent or 0),"smoking_allowed":x.smoking_allowed,"extra_bed_available":x.extra_bed_available,"extra_bed_price":float(x.extra_bed_price) if x.extra_bed_price is not None else None,"extra_bed_information":x.extra_bed_information,"facilities":[{"id":f.id,"name":f.name,"available":f.available} for f in x.facilities],"photos":[{"id":p.id,"url":p.photo_url,"caption":p.caption,"is_primary":p.is_primary,"sort_order":p.sort_order} for p in x.photos]} for x in hotel.room_types]}
def get_hotel_or_404(hotel_id:int,db:Session)->Hotel:
    h=db.query(Hotel).filter(Hotel.id==hotel_id).first()
    if h is None: raise HTTPException(404,"Hotel not found")
    return h
@router.get("/pending")
def get_pending_hotels(db:Session=Depends(get_db),current_user:User=Depends(require_admin)):
    return [serialize_hotel(h) for h in db.query(Hotel).filter(Hotel.status.in_((HotelStatus.PENDING,HotelStatus.AWAITING_TERMS))).order_by(Hotel.created_at.desc()).all()]
@router.get("/live")
def get_live_hotels(db:Session=Depends(get_db),current_user:User=Depends(require_admin)):
    return [serialize_hotel(h) for h in db.query(Hotel).filter(Hotel.status==HotelStatus.APPROVED).order_by(Hotel.created_at.desc()).all()]
@router.get("/")
def get_all_hotels(db:Session=Depends(get_db),current_user:User=Depends(require_admin)):
    return [serialize_hotel(h) for h in db.query(Hotel).order_by(Hotel.created_at.desc()).all()]
@router.get("/{hotel_id}")
def get_hotel_for_admin(hotel_id:int,db:Session=Depends(get_db),current_user:User=Depends(require_admin)): return serialize_hotel(get_hotel_or_404(hotel_id,db))
@router.put("/{hotel_id}")
def update_hotel_for_admin(hotel_id:int,payload:AdminHotelUpdate,db:Session=Depends(get_db),current_user:User=Depends(require_admin)):
    hotel=get_hotel_or_404(hotel_id,db); data=payload.model_dump(exclude_unset=True); property_id=data.pop("property_id",None)
    if property_id is not None:
        if db.query(Hotel).filter(Hotel.property_id==property_id,Hotel.id!=hotel_id).first(): raise HTTPException(400,"Property ID / hotel licence number already exists")
        hotel.property_id=property_id
    for field in ("name","slug","property_type","description","star_rating","email","phone","alternate_phone","website","country","city","address","postal_code","latitude","longitude","total_rooms","check_in_time","check_out_time","timezone","currency","tax_percent","payment_methods","parking_floors","breakfast_options","breakfast_other","property_highlight_floors"):
        if field in data:setattr(hotel,field,data[field])
    facilities=data.get("facilities")
    if facilities is not None:
        for item in list(hotel.facilities):db.delete(item)
        db.flush()
        for item in facilities:
            if str(item.get("name","")).strip():db.add(HotelFacility(hotel_id=hotel.id,name=str(item["name"]).strip(),available=bool(item.get("available",True))))
    policy=data.get("policy")
    if policy is not None:
        if hotel.policy is None:hotel.policy=HotelPolicy(hotel_id=hotel.id)
        for field in ("cancellation_policy","child_policy","pet_policy","smoking_policy","payment_methods","extra_bed_policy","age_restriction","quiet_hours","house_rules"):
            if field in policy:setattr(hotel.policy,field,policy[field])
    documents=data.get("documents")
    if documents is not None:
        for item in documents:
            document_id=item.get("id");document=next((x for x in hotel.documents if x.id==document_id),None) if document_id else None
            if document is None: document=HotelDocument(hotel_id=hotel.id,document_type=str(item.get("type") or item.get("document_type") or "Verification"),document_url=str(item.get("url") or item.get("document_url") or ""),status=str(item.get("status") or "pending"));db.add(document)
            document.document_type=str(item.get("type") or item.get("document_type") or document.document_type);document.license_number=item.get("license_number",document.license_number);document.registration_number=item.get("registration_number",document.registration_number);document.document_number=item.get("document_number",document.document_number);document.document_url=str(item.get("url") or item.get("document_url") or document.document_url);document.status=str(item.get("status") or document.status);document.admin_notes=item.get("admin_notes",document.admin_notes)
        first_license=next((d.license_number.strip() for d in hotel.documents if d.license_number and d.license_number.strip()),None)
        if first_license and (property_id is None or first_license!=hotel.property_id):
            if db.query(Hotel).filter(Hotel.property_id==first_license,Hotel.id!=hotel_id).first():raise HTTPException(400,"Hotel licence number already belongs to another property")
            hotel.property_id=first_license
    photos=data.get("photos")
    if photos is not None:
        for item in photos:
            photo_id=item.get("id");photo=next((x for x in hotel.photos if x.id==photo_id),None) if photo_id else None
            if photo is None:
                if not item.get("url") and not item.get("photo_url"):continue
                photo=HotelPhoto(hotel_id=hotel.id,photo_url=str(item.get("url") or item.get("photo_url")));db.add(photo)
            photo.photo_url=str(item.get("url") or item.get("photo_url") or photo.photo_url);photo.caption=item.get("caption",photo.caption);photo.category=item.get("category",photo.category);photo.is_primary=bool(item.get("is_primary",photo.is_primary));photo.sort_order=int(item.get("sort_order",photo.sort_order or 0))
    room_types=data.get("room_types")
    if room_types is not None:
        for item in room_types:
            room_id=item.get("id");room=next((x for x in hotel.room_types if x.id==room_id),None) if room_id else None
            if room is None:room=RoomType(hotel_id=hotel.id,name=str(item.get("name") or "Room"));db.add(room);db.flush()
            for field in ("name","description","number_of_rooms","max_adults","max_children","bed_type","room_size","base_price","discount_percent","smoking_allowed","extra_bed_available","extra_bed_price","extra_bed_information"):
                if field in item:setattr(room,field,item[field])
            if "facilities" in item:
                for existing in list(room.facilities):db.delete(existing)
                db.flush()
                for facility in item.get("facilities") or []:
                    if str(facility.get("name","")).strip():db.add(RoomTypeFacility(room_type_id=room.id,name=str(facility["name"]).strip(),available=bool(facility.get("available",True))))
            if "photos" in item:
                for photo in item.get("photos") or []:
                    photo_id=photo.get("id");existing=next((x for x in room.photos if x.id==photo_id),None) if photo_id else None
                    if existing is None:
                        if not photo.get("url"):continue
                        existing=RoomTypePhoto(room_type_id=room.id,photo_url=str(photo["url"]));db.add(existing)
                    existing.photo_url=str(photo.get("url") or existing.photo_url);existing.caption=photo.get("caption",existing.caption);existing.is_primary=bool(photo.get("is_primary",existing.is_primary));existing.sort_order=int(photo.get("sort_order",existing.sort_order or 0))
    try:db.commit();db.refresh(hotel)
    except Exception as exc:db.rollback();raise HTTPException(400,f"Property update failed: {exc}") from exc
    return {"message":"Property updated successfully","hotel":serialize_hotel(hotel)}
@router.post("/{hotel_id}/send-back")
def send_back_hotel(hotel_id:int,reason:str=Body(...,embed=True),db:Session=Depends(get_db),current_user:User=Depends(require_admin)):
    hotel=get_hotel_or_404(hotel_id,db)
    if not reason or not reason.strip():raise HTTPException(400,"Rejection reason is required")
    hotel.status=HotelStatus.REJECTED;hotel.rejection_reason=reason.strip();hotel.approved_at=None;hotel.approved_by=None
    if hotel.owner_id:db.add(Notification(user_id=hotel.owner_id,hotel_id=hotel.id,title="Property Changes Required",message=f"Your property was sent back for correction: {hotel.rejection_reason}",type="property_correction_required",read=False))
    db.commit();db.refresh(hotel);return {"message":"Property sent back to owner","hotel":serialize_hotel(hotel)}
@router.post("/{hotel_id}/close")
def close_hotel(hotel_id:int,db:Session=Depends(get_db),current_user:User=Depends(require_admin)):
    hotel=get_hotel_or_404(hotel_id,db);hotel.status=HotelStatus.SUSPENDED;db.commit();db.refresh(hotel);return {"message":"Property closed successfully","hotel":serialize_hotel(hotel)}
@router.delete("/{hotel_id}")
def delete_hotel(hotel_id:int,db:Session=Depends(get_db),current_user:User=Depends(require_admin)):
    hotel=get_hotel_or_404(hotel_id,db);db.delete(hotel);db.commit();return {"message":"Property deleted successfully"}
@router.post("/{hotel_id}/approve")
def approve_hotel(hotel_id:int,db:Session=Depends(get_db),current_user:User=Depends(require_admin)):
    hotel=get_hotel_or_404(hotel_id,db)
    if hotel.status==HotelStatus.APPROVED:raise HTTPException(400,"Hotel is already approved")
    hotel.status=HotelStatus.APPROVED;hotel.rejection_reason=None;hotel.approved_at=datetime.now(timezone.utc);hotel.approved_by=current_user.id;db.commit();db.refresh(hotel);return {"message":"Hotel approved successfully","hotel":serialize_hotel(hotel)}
@router.post("/{hotel_id}/reject")
def reject_hotel(hotel_id:int,reason:str|None=None,db:Session=Depends(get_db),current_user:User=Depends(require_admin)):
    hotel=get_hotel_or_404(hotel_id,db)
    if not reason or not reason.strip():raise HTTPException(400,"Rejection reason is required")
    hotel.status=HotelStatus.REJECTED;hotel.rejection_reason=reason.strip();hotel.approved_at=None;hotel.approved_by=None;db.commit();db.refresh(hotel);return {"message":"Hotel rejected successfully","hotel":serialize_hotel(hotel)}
@router.post("/{hotel_id}/suspend")
def suspend_hotel(hotel_id:int,db:Session=Depends(get_db),current_user:User=Depends(require_admin)):return close_hotel(hotel_id,db,current_user)
@router.post("/{hotel_id}/activate")
def activate_hotel(hotel_id:int,db:Session=Depends(get_db),current_user:User=Depends(require_admin)):
    hotel=get_hotel_or_404(hotel_id,db);hotel.status=HotelStatus.APPROVED;db.commit();db.refresh(hotel);return {"message":"Hotel activated successfully","hotel":serialize_hotel(hotel)}
@router.post("/reset-test-data")
def reset_test_property_data(confirm:str,db:Session=Depends(get_db),current_user:User=Depends(require_admin)):
    if confirm!="RESET_STAYHUB_PROPERTIES":raise HTTPException(400,"Invalid confirmation token")
    hotels=db.query(Hotel).all();deleted_count=len(hotels)
    for hotel in hotels:db.delete(hotel)
    db.commit();return {"message":"All property test data has been reset successfully","deleted_properties":deleted_count,"users_preserved":True,"next_step":"Register a new property from the public List Your Property flow"}
