from datetime import date
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.dependencies import require_hotel_owner
from app.models.reservation import ReservationStatus
from app.models.room_availability import RoomAvailability
from app.models.user import User
from app.schemas.reservation import ReservationCreate, ReservationDateModification, ReservationNoShowRequest, ReservationUpdate
from app.services.commission_service import sync_commission_status
from app.services.reservation_pricing import build_daily_rate_breakdown
from app.services.reservation_service import can_owner_mark_no_show, can_owner_modify_dates, create_reservation, delete_reservation, get_reservation_by_id, get_reservations, mark_reservation_no_show, modify_reservation_dates, update_reservation, no_show_window

router=APIRouter(prefix="/reservations",tags=["Reservations"])

def _reservation_daily_rates(db:Session,reservation):
    room=reservation.room; room_type=room.room_type if room else None; hotel=reservation.hotel
    if not room_type or not hotel:return []
    rows={row.date:{"rate":Decimal(str(row.rate or 0)),"bookable":bool(row.bookable)} for row in db.query(RoomAvailability).filter(RoomAvailability.room_type_id==room_type.id,RoomAvailability.date>=reservation.check_in,RoomAvailability.date<reservation.check_out).all()}
    current=reservation.check_in
    while current<reservation.check_out:
        if current not in rows: rows[current]={"rate":Decimal(str(room_type.base_price or 0)),"bookable":True}
        current=date.fromordinal(current.toordinal()+1)
    return build_daily_rate_breakdown(reservation.check_in,reservation.check_out,rows,Decimal(str(room_type.discount_percent or 0)),Decimal(str(hotel.tax_percent or 0)))

def _property_policy_data(hotel):
    """Expose the property's saved List Your Property policy data to reservation details.

    Empty/unconfigured policy values intentionally remain None so the reservation UI
    can render the single consistent fallback label: Not specified.
    """
    policy=getattr(hotel,"policy",None) if hotel else None
    cancellation=getattr(policy,"cancellation_policy",None) if policy else None
    child=getattr(policy,"child_policy",None) if policy else None
    extra_bed=getattr(policy,"extra_bed_policy",None) if policy else None
    children_extra_bed="; ".join(x for x in (child,extra_bed) if x and str(x).strip()) or None
    parking_floors=getattr(hotel,"parking_floors",None) if hotel else None
    parking=None
    if parking_floors:
        values=[str(x).strip() for x in parking_floors if str(x).strip()]
        if values: parking="Parking available on: "+", ".join(values)
    property_payment=getattr(policy,"payment_methods",None) if policy else None
    if not property_payment:
        selected=getattr(hotel,"payment_methods",None) if hotel else None
        if selected:
            values=[str(x).strip() for x in selected if str(x).strip()]
            property_payment=", ".join(values) if values else None
    return {
        "cancellation_policy": cancellation,
        "prepayment_policy": None,
        "damage_policy": None,
        "children_policy": children_extra_bed,
        "parking_policy": parking,
        "internet_policy": None,
        "pets_policy": getattr(policy,"pet_policy",None) if policy else None,
        "groups_policy": None,
        "property_payment_method": property_payment,
        "smoking_policy": getattr(policy,"smoking_policy",None) if policy else None,
        "age_restriction": getattr(policy,"age_restriction",None) if policy else None,
        "quiet_hours": getattr(policy,"quiet_hours",None) if policy else None,
        "house_rules": getattr(policy,"house_rules",None) if policy else None,
    }

def serialize(reservation,commission_override=None,db=None):
    commission=commission_override if commission_override is not None else reservation.commission
    if reservation.status==ReservationStatus.NO_SHOW and commission and commission.status=="NO_SHOW_WAIVED":
        commissionable_amount=Decimal("0.00"); commission_amount=Decimal("0.00"); owner_amount=Decimal(str(reservation.total_amount or 0)); commission_status="NO_SHOW_WAIVED"
    else:
        commissionable_amount=commission.commissionable_amount if commission else reservation.total_amount; commission_amount=commission.commission_amount if commission else None; owner_amount=commission.owner_amount if commission else None; commission_status=commission.status if commission else None
    guest=reservation.guest; room=reservation.room; room_type=room.room_type if room else None; daily_rates=_reservation_daily_rates(db,reservation) if db is not None else []
    primary_photo=None
    if room_type and getattr(room_type,"photos",None):
        photos=sorted(room_type.photos,key=lambda p:(not bool(p.is_primary),int(p.sort_order or 0),int(p.id or 0)))
        if photos: primary_photo=photos[0].photo_url
    hotel=reservation.hotel; policy_data=_property_policy_data(hotel); no_show_allowed=can_owner_mark_no_show(hotel,reservation) if hotel else False; modification_allowed=can_owner_modify_dates(hotel,reservation) if hotel else False; no_show_start,no_show_end=no_show_window(hotel,reservation) if hotel else (None,None)
    return {"id":reservation.id,"hotel_id":reservation.hotel_id,"guest_id":reservation.guest_id,"room_id":reservation.room_id,"confirmation_no":reservation.confirmation_no,"booking_number":reservation.confirmation_no,"booking_source":reservation.booking_source.value,"check_in":reservation.check_in,"check_out":reservation.check_out,"created_at":reservation.created_at,"received_at":reservation.created_at,"adults":reservation.adults,"children":reservation.children,"room_rate":reservation.room_rate,"discount":reservation.discount,"tax":reservation.tax,"total_amount":reservation.total_amount,"commissionable_amount":commissionable_amount,"status":reservation.status.value,"remarks":reservation.remarks,"payment_method":reservation.payment_method,"property_payment_method":policy_data["property_payment_method"],"payment_status":reservation.payment_status,"payment_reference":reservation.payment_reference,"card_last4":reservation.card_last4,"guest_name":f"{guest.first_name} {guest.last_name}".strip() if guest else None,"guest_phone":guest.phone if guest else None,"guest_email":guest.email if guest else None,"guest_city":guest.city if guest else None,"guest_country":guest.country if guest else None,"guest_nationality":guest.nationality if guest else None,"room_number":room.room_number if room else None,"room_type_id":room_type.id if room_type else None,"room_type_name":room_type.name if room_type else None,"room_description":room_type.description if room_type else None,"room_bed_type":room_type.bed_type if room_type else None,"room_size":room_type.room_size if room_type else None,"max_adults":room_type.max_adults if room_type else None,"max_children":room_type.max_children if room_type else None,"room_photo_url":primary_photo,"included_value_adds":[],"meal_options":[],"total_units":1,"daily_rates":daily_rates,"commission_percent":commission.commission_percent if commission else None,"commission_amount":commission_amount,"owner_amount":owner_amount,"commission_status":commission_status,"no_show_allowed":no_show_allowed,"no_show_start_at":no_show_start,"no_show_end_at":no_show_end,"modification_allowed":modification_allowed,**policy_data}

@router.post("/hotel/{hotel_id}",status_code=status.HTTP_201_CREATED)
def create(hotel_id:int,reservation:ReservationCreate,db:Session=Depends(get_db)):
    try:return serialize(create_reservation(db=db,hotel_id=hotel_id,reservation=reservation),db=db)
    except ValueError as e:raise HTTPException(status_code=400,detail=str(e))

@router.get("/hotel/{hotel_id}")
def get_all(hotel_id:int,db:Session=Depends(get_db)):
    serialized=[]
    for item in get_reservations(db=db,hotel_id=hotel_id):
        commission=sync_commission_status(db,item); serialized.append(serialize(item,commission_override=commission,db=db))
    db.commit(); return serialized

@router.get("/{reservation_id}")
def get_one(reservation_id:int,db:Session=Depends(get_db)):
    reservation=get_reservation_by_id(db=db,reservation_id=reservation_id)
    if reservation is None:raise HTTPException(status_code=404,detail="Reservation not found")
    commission=sync_commission_status(db,reservation); db.commit(); return serialize(reservation,commission_override=commission,db=db)

@router.post("/{reservation_id}/owner/no-show")
def owner_no_show(reservation_id:int,payload:ReservationNoShowRequest,db:Session=Depends(get_db),current_user:User=Depends(require_hotel_owner)):
    reservation=get_reservation_by_id(db=db,reservation_id=reservation_id)
    if reservation is None:raise HTTPException(status_code=404,detail="Reservation not found")
    if reservation.hotel.owner_id!=current_user.id:raise HTTPException(status_code=403,detail="Reservation does not belong to your property")
    try:
        updated,commission=mark_reservation_no_show(db,reservation,payload.waive_fee); return serialize(updated,commission_override=commission,db=db)
    except ValueError as e:raise HTTPException(status_code=400,detail=str(e))

@router.post("/{reservation_id}/owner/modify")
def owner_modify(reservation_id:int,payload:ReservationDateModification,db:Session=Depends(get_db),current_user:User=Depends(require_hotel_owner)):
    reservation=get_reservation_by_id(db=db,reservation_id=reservation_id)
    if reservation is None:raise HTTPException(status_code=404,detail="Reservation not found")
    if reservation.hotel.owner_id!=current_user.id:raise HTTPException(status_code=403,detail="Reservation does not belong to your property")
    try:
        updated=modify_reservation_dates(db,reservation,payload.check_in,payload.check_out); commission=sync_commission_status(db,updated); db.commit(); return serialize(updated,commission_override=commission,db=db)
    except ValueError as e:raise HTTPException(status_code=400,detail=str(e))

@router.put("/{reservation_id}")
def update(reservation_id:int,reservation:ReservationUpdate,db:Session=Depends(get_db)):
    db_reservation=get_reservation_by_id(db=db,reservation_id=reservation_id)
    if db_reservation is None:raise HTTPException(status_code=404,detail="Reservation not found")
    try:return serialize(update_reservation(db=db,db_reservation=db_reservation,reservation=reservation),db=db)
    except ValueError as e:raise HTTPException(status_code=400,detail=str(e))

@router.delete("/{reservation_id}")
def delete(reservation_id:int,db:Session=Depends(get_db)):
    db_reservation=get_reservation_by_id(db=db,reservation_id=reservation_id)
    if db_reservation is None:raise HTTPException(status_code=404,detail="Reservation not found")
    delete_reservation(db=db,db_reservation=db_reservation); return {"message":"Reservation deleted successfully"}
