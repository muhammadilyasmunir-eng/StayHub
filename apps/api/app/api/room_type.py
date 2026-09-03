from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from pathlib import Path
from uuid import uuid4

from app.dependencies import get_db, get_current_user
from app.models.room_type_photo import RoomTypePhoto
from app.models.user import User
from app.schemas.room_type import RoomTypeCreate, RoomTypeUpdate, RoomTypeResponse
from app.services.hotel_service import get_hotel_by_id
from app.services.room_type_service import create_room_type, get_room_types, get_room_type_by_id, update_room_type, delete_room_type

router = APIRouter(prefix="/room-types", tags=["Room Types"])

UPLOAD_ROOT = Path(__file__).resolve().parent.parent / "static" / "uploads" / "room-types"
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
MAX_FILE_SIZE = 10 * 1024 * 1024
MIN_ROOM_PHOTOS = 3
MAX_ROOM_PHOTOS = 10


def _owner_room_type(db: Session, room_type_id: int, current_user: User):
    room_type = get_room_type_by_id(db, room_type_id)
    if room_type is None:
        raise HTTPException(status_code=404, detail="Room type not found")
    hotel = get_hotel_by_id(db, room_type.hotel_id)
    if hotel is None or hotel.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Room type not found")
    return room_type


def _validate_upload_count(existing: int, incoming: int) -> None:
    if incoming < 1:
        raise HTTPException(status_code=400, detail="At least 1 room photo must be selected.")
    if existing == 0 and incoming < MIN_ROOM_PHOTOS:
        raise HTTPException(status_code=400, detail=f"Minimum {MIN_ROOM_PHOTOS} room photos are required for a new room category.")
    if existing + incoming > MAX_ROOM_PHOTOS:
        raise HTTPException(status_code=400, detail=f"Maximum {MAX_ROOM_PHOTOS} photos are allowed. This room category already has {existing} photo(s).")


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
    if room_type.number_of_rooms is not None:
        photo_count = db.query(RoomTypePhoto).filter(RoomTypePhoto.room_type_id == db_room_type.id).count()
        if photo_count < MIN_ROOM_PHOTOS:
            raise HTTPException(status_code=400, detail=f"At least {MIN_ROOM_PHOTOS} room photos are required before saving this room category.")
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
    _validate_upload_count(existing, len(files))

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


@router.put("/{room_type_id}/photos/{photo_id}")
async def replace_photo(room_type_id: int, photo_id: int, file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    room_type = _owner_room_type(db, room_type_id, current_user)
    photo = db.query(RoomTypePhoto).filter(RoomTypePhoto.id == photo_id, RoomTypePhoto.room_type_id == room_type.id).first()
    if photo is None:
        raise HTTPException(status_code=404, detail="Photo not found")
    extension = Path(file.filename or "").suffix.lower()
    if extension not in IMAGE_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only JPG, JPEG, PNG, WEBP and GIF images are allowed.")
    content = await file.read(MAX_FILE_SIZE + 1)
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="Each room photo must be 10 MB or smaller.")
    filename = f"{uuid4().hex}{extension}"
    UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)
    (UPLOAD_ROOT / filename).write_bytes(content)
    old_url = str(photo.photo_url or "")
    photo.photo_url = f"/static/uploads/room-types/{filename}"
    photo.caption = file.filename
    db.commit()
    db.refresh(photo)
    if "/static/" in old_url:
        old_relative = old_url.split("/static/", 1)[1]
        old_file = Path(__file__).resolve().parent.parent / "static" / old_relative
        try:
            old_file.unlink(missing_ok=True)
        except OSError:
            pass
    return photo


@router.delete("/{room_type_id}/photos/{photo_id}")
def delete_photo(room_type_id: int, photo_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    room_type = _owner_room_type(db, room_type_id, current_user)
    photo = db.query(RoomTypePhoto).filter(RoomTypePhoto.id == photo_id, RoomTypePhoto.room_type_id == room_type.id).first()
    if photo is None:
        raise HTTPException(status_code=404, detail="Photo not found")
    remaining = db.query(RoomTypePhoto).filter(RoomTypePhoto.room_type_id == room_type.id).count()
    if remaining <= MIN_ROOM_PHOTOS:
        raise HTTPException(status_code=400, detail=f"A minimum of {MIN_ROOM_PHOTOS} room photos must be kept.")
    db.delete(photo)
    db.commit()
    return {"message": "Photo deleted successfully"}
