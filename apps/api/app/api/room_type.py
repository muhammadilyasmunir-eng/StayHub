from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from pathlib import Path
from uuid import uuid4

from app.dependencies import get_db, get_current_user
from app.models.hotel import Hotel
from app.models.room_type_photo import RoomTypePhoto
from app.models.user import User
from app.schemas.room_type import RoomTypeCreate, RoomTypeUpdate, RoomTypeResponse
from app.services.hotel_service import get_hotel_by_id
from app.services.room_type_service import create_room_type, get_room_types, get_room_type_by_id, update_room_type, delete_room_type

router = APIRouter(prefix="/room-types", tags=["Room Types"])

UPLOAD_ROOT = Path("app/static/uploads/room-types")
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
MAX_FILE_SIZE = 10 * 1024 * 1024


def _owner_room_type(db: Session, room_type_id: int, current_user: User):
    room_type = get_room_type_by_id(db, room_type_id)
    if room_type is None:
        raise HTTPException(status_code=404, detail="Room type not found")
    hotel = get_hotel_by_id(db, room_type.hotel_id)
    if hotel is None or hotel.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Room type not found")
    return room_type


@router.post("/hotel/{hotel_id}", response_model=RoomTypeResponse, status_code=status.HTTP_201_CREATED)
def create(hotel_id: int, room_type: RoomTypeCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    hotel = get_hotel_by_id(db, hotel_id)
    if hotel is None or hotel.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Hotel not found")
    return create_room_type(db=db, room_type=room_type, hotel_id=hotel.id)


@router.get("/hotel/{hotel_id}", response_model=list[RoomTypeResponse])
def list_room_types(hotel_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    hotel = get_hotel_by_id(db, hotel_id)
    if hotel is None or hotel.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Hotel not found")
    return get_room_types(db=db, hotel_id=hotel.id)


@router.get("/{room_type_id}", response_model=RoomTypeResponse)
def get_room_type(room_type_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return _owner_room_type(db, room_type_id, current_user)


@router.put("/{room_type_id}", response_model=RoomTypeResponse)
def update(room_type_id: int, room_type: RoomTypeUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_room_type = _owner_room_type(db, room_type_id, current_user)
    return update_room_type(db=db, db_room_type=db_room_type, room_type=room_type)


@router.delete("/{room_type_id}")
def delete(room_type_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_room_type = _owner_room_type(db, room_type_id, current_user)
    delete_room_type(db=db, db_room_type=db_room_type)
    return {"message": "Room type deleted successfully"}


@router.get("/{room_type_id}/photos")
def list_photos(room_type_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    room_type = _owner_room_type(db, room_type_id, current_user)
    return db.query(RoomTypePhoto).filter(RoomTypePhoto.room_type_id == room_type.id).order_by(RoomTypePhoto.sort_order, RoomTypePhoto.id).all()


@router.post("/{room_type_id}/photos")
async def upload_photos(room_type_id: int, files: list[UploadFile] = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    room_type = _owner_room_type(db, room_type_id, current_user)
    existing = db.query(RoomTypePhoto).filter(RoomTypePhoto.room_type_id == room_type.id).count()
    if len(files) < 3:
        raise HTTPException(status_code=400, detail="Minimum 3 room photos are required.")
    if existing + len(files) > 4:
        raise HTTPException(status_code=400, detail=f"Maximum 4 photos are allowed. This room category already has {existing} photo(s).")

    UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)
    created = []
    for index, file in enumerate(files):
        extension = Path(file.filename or "").suffix.lower()
        if extension not in IMAGE_EXTENSIONS:
            raise HTTPException(status_code=400, detail="Only JPG, JPEG, PNG, WEBP and GIF images are allowed.")
        content = await file.read(MAX_FILE_SIZE + 1)
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="Each room photo must be 10 MB or smaller.")
        filename = f"{uuid4().hex}{extension}"
        (UPLOAD_ROOT / filename).write_bytes(content)
        photo = RoomTypePhoto(room_type_id=room_type.id, photo_url=f"/static/uploads/room-types/{filename}", caption=file.filename, is_primary=(existing == 0 and index == 0), sort_order=existing + index)
        db.add(photo)
        created.append(photo)
    db.commit()
    for photo in created:
        db.refresh(photo)
    return created


@router.delete("/{room_type_id}/photos/{photo_id}")
def delete_photo(room_type_id: int, photo_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    room_type = _owner_room_type(db, room_type_id, current_user)
    photo = db.query(RoomTypePhoto).filter(RoomTypePhoto.id == photo_id, RoomTypePhoto.room_type_id == room_type.id).first()
    if photo is None:
        raise HTTPException(status_code=404, detail="Photo not found")
    remaining = db.query(RoomTypePhoto).filter(RoomTypePhoto.room_type_id == room_type.id).count()
    if remaining <= 3:
        raise HTTPException(status_code=400, detail="A minimum of 3 room photos must be kept.")
    db.delete(photo)
    db.commit()
    return {"message": "Photo deleted successfully"}
