from datetime import datetime
from enum import Enum
from sqlalchemy import DateTime, ForeignKey, String, Text, Float, Integer, Numeric, JSON, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class HotelStatus(str, Enum):
    PENDING="pending"; APPROVED="approved"; AWAITING_TERMS="awaiting_terms"; REJECTED="rejected"; SUSPENDED="suspended"; INACTIVE="inactive"

class Hotel(Base):
    __tablename__="hotels"
    id: Mapped[int]=mapped_column(primary_key=True,index=True)
    owner_id: Mapped[int|None]=mapped_column(ForeignKey("users.id",ondelete="SET NULL"),nullable=True)
    property_id: Mapped[str]=mapped_column(String(50),unique=True,index=True,nullable=False)
    name: Mapped[str]=mapped_column(String(255),nullable=False); slug: Mapped[str]=mapped_column(String(255),unique=True,index=True,nullable=False)
    property_type: Mapped[str]=mapped_column(String(100),default="Hotel",nullable=False); description: Mapped[str|None]=mapped_column(Text,nullable=True)
    star_rating: Mapped[float|None]=mapped_column(Float,nullable=True); email: Mapped[str]=mapped_column(String(255),unique=True,nullable=False); phone: Mapped[str]=mapped_column(String(50),nullable=False)
    alternate_phone: Mapped[str|None]=mapped_column(String(50),nullable=True); website: Mapped[str|None]=mapped_column(String(500),nullable=True)
    country: Mapped[str]=mapped_column(String(100),nullable=False); city: Mapped[str]=mapped_column(String(100),nullable=False); address: Mapped[str]=mapped_column(String(500),nullable=False); postal_code: Mapped[str|None]=mapped_column(String(30),nullable=True)
    latitude: Mapped[float|None]=mapped_column(Float,nullable=True); longitude: Mapped[float|None]=mapped_column(Float,nullable=True); total_rooms: Mapped[int]=mapped_column(Integer,default=0,nullable=False)
    check_in_time: Mapped[str]=mapped_column(String(10),default="14:00",nullable=False); check_out_time: Mapped[str]=mapped_column(String(10),default="12:00",nullable=False); timezone: Mapped[str]=mapped_column(String(100),default="Asia/Karachi",nullable=False); currency: Mapped[str]=mapped_column(String(10),default="PKR",nullable=False)
    tax_percent: Mapped[float|None]=mapped_column(Numeric(5,2),nullable=True); commission_percent: Mapped[float|None]=mapped_column(Numeric(5,2),nullable=True)
    status: Mapped[HotelStatus]=mapped_column(default=HotelStatus.PENDING,nullable=False,index=True)
    rejection_reason: Mapped[str|None]=mapped_column(String(1000),nullable=True); approved_at: Mapped[datetime|None]=mapped_column(DateTime(timezone=True),nullable=True); approved_by: Mapped[int|None]=mapped_column(ForeignKey("users.id",ondelete="SET NULL"),nullable=True)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now(),nullable=False); updated_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now(),nullable=False)
    payment_methods: Mapped[list[str]]=mapped_column(JSON,default=list,nullable=False); parking_floors: Mapped[list[str]]=mapped_column(JSON,default=list,nullable=False); breakfast_options: Mapped[list[str]]=mapped_column(JSON,default=list,nullable=False); breakfast_other: Mapped[str|None]=mapped_column(Text,nullable=True); property_highlight_floors: Mapped[list[int]]=mapped_column(JSON,default=list,nullable=False)
    invoice_overdue: Mapped[bool]=mapped_column(Boolean,default=False,nullable=False,index=True); duplicate_rejection: Mapped[bool]=mapped_column(Boolean,default=False,nullable=False,index=True)
    owner_cnic_front_url: Mapped[str|None]=mapped_column(String(1000),nullable=True)
    owner_cnic_back_url: Mapped[str|None]=mapped_column(String(1000),nullable=True)
    signed_agreement_url: Mapped[str|None]=mapped_column(String(1000),nullable=True)
    agreement_submitted_at: Mapped[datetime|None]=mapped_column(DateTime(timezone=True),nullable=True)
    owner_documents_submitted: Mapped[bool]=mapped_column(Boolean,default=False,nullable=False,index=True)
    owner: Mapped["User|None"]=relationship("User",foreign_keys=[owner_id],back_populates="hotels"); approver: Mapped["User|None"]=relationship("User",foreign_keys=[approved_by]); room_types: Mapped[list["RoomType"]]=relationship("RoomType",back_populates="hotel",cascade="all, delete-orphan"); guests: Mapped[list["Guest"]]=relationship("Guest",back_populates="hotel",cascade="all, delete-orphan"); reservations: Mapped[list["Reservation"]]=relationship("Reservation",back_populates="hotel",cascade="all, delete-orphan"); facilities: Mapped[list["HotelFacility"]]=relationship("HotelFacility",back_populates="hotel",cascade="all, delete-orphan"); photos: Mapped[list["HotelPhoto"]]=relationship("HotelPhoto",back_populates="hotel",cascade="all, delete-orphan"); policy: Mapped["HotelPolicy|None"]=relationship("HotelPolicy",back_populates="hotel",uselist=False,cascade="all, delete-orphan"); documents: Mapped[list["HotelDocument"]]=relationship("HotelDocument",back_populates="hotel",cascade="all, delete-orphan")
