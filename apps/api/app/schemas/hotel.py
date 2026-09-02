from decimal import Decimal
from pydantic import BaseModel, EmailStr, ConfigDict, Field, field_validator
from app.models.hotel import HotelStatus

PAYMENT_METHODS={"Cash","Credit Card","Debit Card"}
BREAKFAST_OPTIONS={"Continental","American","Asian","Buffet","Pakistani"}

def validate_floors(value):
    values=value or []
    for floor in values:
        if isinstance(floor,int):
            if floor<1 or floor>200: raise ValueError("Floor numbers must be between 1 and 200")
        elif str(floor) not in {"Ground","Basement"}: raise ValueError("Parking floors may be Ground, Basement, or 1-200")
    return list(dict.fromkeys(values))

class HotelCreate(BaseModel):
    property_id: str = Field(min_length=6,pattern=r"^\d{6,}$")
    name:str; slug:str; email:EmailStr; phone:str; country:str; city:str; address:str
    timezone:str="Asia/Karachi"; currency:str="PKR"; tax_percent:Decimal|None=Field(default=None,ge=0,le=100)

# Billing configuration is platform-admin controlled. Owners can view these values via HotelResponse only.
class HotelUpdate(BaseModel):
    name:str|None=None; slug:str|None=None; email:EmailStr|None=None; phone:str|None=None; country:str|None=None; city:str|None=None; address:str|None=None
    timezone:str|None=None; currency:str|None=None; property_type:str|None=None; description:str|None=None
    star_rating:float|None=Field(default=None,ge=0,le=5); alternate_phone:str|None=None; website:str|None=None; postal_code:str|None=None
    latitude:float|None=Field(default=None,ge=-90,le=90); longitude:float|None=Field(default=None,ge=-180,le=180); total_rooms:int|None=Field(default=None,ge=0)
    check_in_time:str|None=None; check_out_time:str|None=None

class AdminHotelUpdate(BaseModel):
    property_id:str|None=Field(default=None,min_length=6,pattern=r"^\d{6,}$"); name:str|None=Field(default=None,min_length=2,max_length=255); slug:str|None=Field(default=None,min_length=2,max_length=255,pattern=r"^[a-z0-9-]+$")
    property_type:str|None=None; description:str|None=None; star_rating:float|None=Field(default=None,ge=0,le=5); email:EmailStr|None=None; phone:str|None=Field(default=None,min_length=7,max_length=50); alternate_phone:str|None=None; website:str|None=None; country:str|None=None; city:str|None=None; address:str|None=None; postal_code:str|None=None; latitude:float|None=Field(default=None,ge=-90,le=90); longitude:float|None=Field(default=None,ge=-180,le=180); total_rooms:int|None=Field(default=None,ge=0); check_in_time:str|None=None; check_out_time:str|None=None; timezone:str|None=None; currency:str|None=None; tax_percent:Decimal|None=Field(default=None,ge=0,le=100); payment_methods:list[str]|None=None; parking_floors:list[str|int]|None=None; breakfast_options:list[str]|None=None; breakfast_other:str|None=None; property_highlight_floors:list[int]|None=None; facilities:list[dict]|None=None; policy:dict|None=None; documents:list[dict]|None=None; room_types:list[dict]|None=None; photos:list[dict]|None=None
    @field_validator("payment_methods")
    @classmethod
    def valid_payment_methods(cls,value):
        if value is not None and any(x not in PAYMENT_METHODS for x in value): raise ValueError("Payment methods must be Cash, Credit Card, or Debit Card")
        return list(dict.fromkeys(value or []))
    @field_validator("parking_floors")
    @classmethod
    def valid_parking_floors(cls,value): return validate_floors(value)
    @field_validator("breakfast_options")
    @classmethod
    def valid_breakfast_options(cls,value):
        if value is not None and any(x not in BREAKFAST_OPTIONS for x in value): raise ValueError("Unsupported breakfast option")
        return list(dict.fromkeys(value or []))
    @field_validator("property_highlight_floors")
    @classmethod
    def valid_highlight_floors(cls,value):
        values=value or []
        if any(x<1 or x>200 for x in values): raise ValueError("Property highlight floors must be between 1 and 200")
        return list(dict.fromkeys(values))

class FacilityResponse(BaseModel):
    id:int; name:str; description:str|None=None; available:bool=True
    model_config=ConfigDict(from_attributes=True)
class PolicyResponse(BaseModel):
    cancellation_policy:str|None=None; child_policy:str|None=None; pet_policy:str|None=None; smoking_policy:str|None=None; payment_methods:str|None=None; extra_bed_policy:str|None=None; age_restriction:str|None=None; quiet_hours:str|None=None; house_rules:str|None=None
    model_config=ConfigDict(from_attributes=True)
class PhotoResponse(BaseModel):
    id:int; photo_url:str; caption:str|None=None; category:str|None=None; is_primary:bool=False; sort_order:int=0
    model_config=ConfigDict(from_attributes=True)
class DocumentResponse(BaseModel):
    id:int; document_type:str; license_number:str|None=None; registration_number:str|None=None; document_number:str|None=None; document_url:str; status:str; admin_notes:str|None=None
    model_config=ConfigDict(from_attributes=True)
class RoomFacilityResponse(BaseModel):
    id:int; name:str; available:bool=True
    model_config=ConfigDict(from_attributes=True)
class RoomPhotoResponse(BaseModel):
    id:int; photo_url:str; caption:str|None=None; is_primary:bool=False; sort_order:int=0
    model_config=ConfigDict(from_attributes=True)
class RoomTypeResponse(BaseModel):
    id:int; name:str; description:str|None=None; number_of_rooms:int=1; max_adults:int=2; max_children:int=0; bed_type:str|None=None; room_size:str|None=None; base_price:Decimal=0; discount_percent:Decimal=0; smoking_allowed:bool=False; extra_bed_available:bool=False; extra_bed_price:Decimal|None=None; extra_bed_information:str|None=None; status:bool=True; facilities:list[RoomFacilityResponse]=[]; photos:list[RoomPhotoResponse]=[]
    model_config=ConfigDict(from_attributes=True)
class OwnerResponse(BaseModel):
    id:int; full_name:str; email:EmailStr; phone:str|None=None; username:str|None=None
    model_config=ConfigDict(from_attributes=True)

class HotelResponse(BaseModel):
    id:int; property_id:str; owner_id: int | None = None; name:str; slug:str; property_type:str="Hotel"; description:str|None=None; star_rating:float|None=None; email:EmailStr; phone:str; alternate_phone:str|None=None; website:str|None=None; country:str; city:str; address:str; postal_code:str|None=None; latitude:float|None=None; longitude:float|None=None; total_rooms:int=0; check_in_time:str="14:00"; check_out_time:str="12:00"; timezone:str; currency:str; tax_percent:Decimal|None=None; commission_percent:Decimal|None=None; status:HotelStatus; rejection_reason:str|None=None; approved_at:object|None=None; created_at: object | None = None; payment_methods:list[str]=[]; parking_floors:list[str]=[]; breakfast_options:list[str]=[]; breakfast_other:str|None=None; property_highlight_floors:list[int]=[]; facilities:list[FacilityResponse]=[]; policy:PolicyResponse|None=None; documents:list[DocumentResponse]=[]; photos:list[PhotoResponse]=[]; room_types:list[RoomTypeResponse]=[]; owner:OwnerResponse|None=None
    model_config=ConfigDict(from_attributes=True)
