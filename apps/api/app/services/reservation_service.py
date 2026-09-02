from datetime import date, datetime, time, timedelta
from decimal import Decimal, ROUND_HALF_UP
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session
from app.models.guest import Guest
from app.models.hotel import Hotel
from app.models.reservation import BookingSource as ModelBookingSource, Reservation, ReservationStatus
from app.models.room import Room, RoomStatus
from app.models.room_type import RoomType
from app.schemas.reservation import ReservationCreate, ReservationUpdate
from app.services.commission_service import apply_no_show_commission, create_commission, sync_commission_status


def _model_booking_source(value):
    if isinstance(value, ModelBookingSource): return value
    return ModelBookingSource[value.name]

def generate_confirmation_number(db: Session) -> str:
    total=db.query(Reservation).count()+1; number=10000000+(total%90000000)
    while db.query(Reservation).filter(Reservation.confirmation_no==str(number)).first() is not None:
        number += 1
        if number>99999999: number=10000000
    return str(number)

def calculate_total(room_rate: Decimal, discount: Decimal, tax: Decimal, check_in: date, check_out: date) -> Decimal:
    nights=(check_out-check_in).days
    if nights<=0: raise ValueError("Check-out date must be after check-in date")
    return max(room_rate*nights-discount+tax,Decimal("0.00"))

def get_reservation_by_id(db: Session, reservation_id: int): return db.query(Reservation).filter(Reservation.id==reservation_id).first()
def get_reservations(db: Session, hotel_id: int): return db.query(Reservation).filter(Reservation.hotel_id==hotel_id).order_by(Reservation.id.desc()).all()

def room_is_available(db: Session, room_id: int, check_in: date, check_out: date, exclude_reservation_id: int|None=None) -> bool:
    query=db.query(Reservation).filter(Reservation.room_id==room_id,Reservation.check_in<check_out,Reservation.check_out>check_in,Reservation.status.notin_([ReservationStatus.CANCELLED,ReservationStatus.NO_SHOW]))
    if exclude_reservation_id is not None: query=query.filter(Reservation.id!=exclude_reservation_id)
    return query.first() is None

def _hotel_zone(hotel: Hotel)->ZoneInfo:
    try: return ZoneInfo(hotel.timezone or "Asia/Karachi")
    except Exception: return ZoneInfo("Asia/Karachi")

def _hotel_datetime(hotel: Hotel, stay_date: date, time_value: str, default: str)->datetime:
    raw=(time_value or default).strip()
    try: hh,mm=raw.split(":",1); hh_i,mm_i=int(hh),int(mm)
    except Exception: hh_i,mm_i=map(int,default.split(":",1))
    return datetime.combine(stay_date,time(hh_i,mm_i),tzinfo=_hotel_zone(hotel))

def no_show_window(hotel: Hotel, reservation: Reservation, now: datetime|None=None)->tuple[datetime,datetime]:
    checkout=_hotel_datetime(hotel,reservation.check_out,hotel.check_out_time,"12:00"); return checkout,checkout+timedelta(hours=48)

def can_owner_mark_no_show(hotel: Hotel,reservation: Reservation,now:datetime|None=None)->bool:
    start,end=no_show_window(hotel,reservation,now); current=now.astimezone(_hotel_zone(hotel)) if now else datetime.now(_hotel_zone(hotel)); return reservation.status in [ReservationStatus.CONFIRMED,ReservationStatus.CHECKED_IN,ReservationStatus.CHECKED_OUT] and start<=current<=end

def modify_access_window(hotel: Hotel, reservation: Reservation)->tuple[datetime,datetime]:
    """Owner modify window: reservation creation time through 24h after checkout at noon."""
    zone=_hotel_zone(hotel)
    created=reservation.created_at
    start=created.replace(tzinfo=zone) if created.tzinfo is None else created.astimezone(zone)
    checkout=_hotel_datetime(hotel,reservation.check_out,hotel.check_out_time,"12:00")
    return start, checkout + timedelta(hours=24)

def can_owner_modify_dates(hotel: Hotel,reservation: Reservation,now:datetime|None=None)->bool:
    zone=_hotel_zone(hotel); current=now.astimezone(zone) if now else datetime.now(zone); start,end=modify_access_window(hotel,reservation); return reservation.status in [ReservationStatus.CONFIRMED,ReservationStatus.CHECKED_IN] and start<=current<=end

def create_reservation(db:Session,hotel_id:int,reservation:ReservationCreate):
    if reservation.check_out<=reservation.check_in: raise ValueError("Check-out date must be after check-in date")
    hotel=db.query(Hotel).filter(Hotel.id==hotel_id).first()
    if hotel is None: raise ValueError("Hotel not found")
    guest=db.query(Guest).filter(Guest.id==reservation.guest_id,Guest.hotel_id==hotel_id).first()
    if guest is None: raise ValueError("Guest not found")
    room=db.query(Room).join(RoomType,RoomType.id==Room.room_type_id).filter(Room.id==reservation.room_id,RoomType.hotel_id==hotel_id,Room.active.is_(True)).first()
    if room is None: raise ValueError("Room not found or inactive")
    if room.status in [RoomStatus.MAINTENANCE,RoomStatus.OUT_OF_ORDER]: raise ValueError("Room is not available for booking")
    if not room_is_available(db,reservation.room_id,reservation.check_in,reservation.check_out): raise ValueError("Room is already booked for the selected dates")
    total_amount=calculate_total(reservation.room_rate,reservation.discount,reservation.tax,reservation.check_in,reservation.check_out)
    db_reservation=Reservation(hotel_id=hotel_id,guest_id=reservation.guest_id,room_id=reservation.room_id,confirmation_no=generate_confirmation_number(db),booking_source=_model_booking_source(reservation.booking_source),check_in=reservation.check_in,check_out=reservation.check_out,adults=reservation.adults,children=reservation.children,room_rate=reservation.room_rate,discount=reservation.discount,tax=reservation.tax,total_amount=total_amount,status=ReservationStatus.CONFIRMED,remarks=reservation.remarks)
    db.add(db_reservation); room.status=RoomStatus.RESERVED
    try: db.flush(); create_commission(db,db_reservation); db.commit()
    except Exception: db.rollback(); raise
    db.refresh(db_reservation); return db_reservation

def update_reservation(db:Session,db_reservation:Reservation,reservation:ReservationUpdate):
    update_data=reservation.model_dump(exclude_unset=True); new_check_in=update_data.get("check_in",db_reservation.check_in); new_check_out=update_data.get("check_out",db_reservation.check_out)
    if new_check_out<=new_check_in: raise ValueError("Check-out date must be after check-in date")
    if not room_is_available(db,db_reservation.room_id,new_check_in,new_check_out,db_reservation.id): raise ValueError("Room is already booked for the selected dates")
    if "booking_source" in update_data and update_data["booking_source"] is not None: update_data["booking_source"]=_model_booking_source(update_data["booking_source"])
    for key,value in update_data.items(): setattr(db_reservation,key,value)
    db_reservation.total_amount=calculate_total(db_reservation.room_rate,db_reservation.discount,db_reservation.tax,db_reservation.check_in,db_reservation.check_out)
    room=db.query(Room).filter(Room.id==db_reservation.room_id).first()
    if room:
        room.status=RoomStatus.AVAILABLE if db_reservation.status in [ReservationStatus.CANCELLED,ReservationStatus.NO_SHOW] else RoomStatus.OCCUPIED if db_reservation.status==ReservationStatus.CHECKED_IN else RoomStatus.DIRTY if db_reservation.status==ReservationStatus.CHECKED_OUT else RoomStatus.RESERVED
    try: sync_commission_status(db,db_reservation); db.commit()
    except Exception: db.rollback(); raise
    db.refresh(db_reservation); return db_reservation

def modify_reservation_dates(db:Session,db_reservation:Reservation,new_check_in:date,new_check_out:date):
    hotel=db_reservation.hotel
    if not can_owner_modify_dates(hotel,db_reservation): raise ValueError("Reservation modification is only available from booking time until 24 hours after checkout")
    if new_check_out<=new_check_in: raise ValueError("Check-out date must be after check-in date")
    if not room_is_available(db,db_reservation.room_id,new_check_in,new_check_out,db_reservation.id): raise ValueError("Room is already booked for the selected dates")
    old_nights=max(1,(db_reservation.check_out-db_reservation.check_in).days); new_nights=(new_check_out-new_check_in).days
    discount_per_night=Decimal(str(db_reservation.discount or 0))/Decimal(old_nights); tax_per_night=Decimal(str(db_reservation.tax or 0))/Decimal(old_nights)
    db_reservation.check_in=new_check_in; db_reservation.check_out=new_check_out
    db_reservation.discount=(discount_per_night*Decimal(new_nights)).quantize(Decimal("0.01"),rounding=ROUND_HALF_UP)
    db_reservation.tax=(tax_per_night*Decimal(new_nights)).quantize(Decimal("0.01"),rounding=ROUND_HALF_UP)
    db_reservation.total_amount=calculate_total(Decimal(str(db_reservation.room_rate or 0)),db_reservation.discount,db_reservation.tax,new_check_in,new_check_out)
    sync_commission_status(db,db_reservation); db.commit(); db.refresh(db_reservation); return db_reservation

def mark_reservation_no_show(db:Session,db_reservation:Reservation,waive_fee:bool):
    hotel=db_reservation.hotel
    if not can_owner_mark_no_show(hotel,db_reservation): raise ValueError("No-show is only available from checkout time until 48 hours after checkout")
    db_reservation.status=ReservationStatus.NO_SHOW
    room=db.query(Room).filter(Room.id==db_reservation.room_id).first()
    if room: room.status=RoomStatus.AVAILABLE
    commission=apply_no_show_commission(db,db_reservation,waive_fee); db.commit(); db.refresh(db_reservation); return db_reservation,commission

def delete_reservation(db:Session,db_reservation:Reservation):
    room=db.query(Room).filter(Room.id==db_reservation.room_id).first()
    if room: room.status=RoomStatus.AVAILABLE
    db.delete(db_reservation)
    try: db.commit()
    except Exception: db.rollback(); raise
    return True
