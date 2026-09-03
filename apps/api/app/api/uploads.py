from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies import get_current_user, require_admin
from app.models.hotel import Hotel
from app.models.hotel_document import HotelDocument
from app.models.hotel_photo import HotelPhoto
from app.models.user import User, UserRole

router = APIRouter(prefix="/uploads", tags=["Uploads"])

UPLOAD_ROOT = Path(__file__).resolve().parent.parent / "static" / "uploads"
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
DOCUMENT_EXTENSIONS = {".pdf", ".doc", ".docx", ".xls", ".xlsx"}
ALLOWED_EXTENSIONS = IMAGE_EXTENSIONS | DOCUMENT_EXTENSIONS
MAX_FILE_SIZE = 10 * 1024 * 1024


def _validate_file(file: UploadFile) -> str:
    if not file.filename: raise HTTPException(status_code=400, detail="File name is required.")
    extension = Path(file.filename).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS: raise HTTPException(status_code=400, detail="Unsupported file type.")
    return extension


async def _save_file(file: UploadFile, extension: str) -> tuple[str, int]:
    content = await file.read(MAX_FILE_SIZE + 1)
    if len(content) > MAX_FILE_SIZE: raise HTTPException(status_code=413, detail="File is too large. Maximum size is 10 MB.")
    UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)
    safe_name = f"{uuid4().hex}{extension}"
    (UPLOAD_ROOT / safe_name).write_bytes(content)
    return f"/static/uploads/{safe_name}", len(content)


@router.post("/registration", status_code=status.HTTP_201_CREATED)
async def upload_registration_file(file: UploadFile = File(...)):
    extension = _validate_file(file); url, size = await _save_file(file, extension)
    return {"url": url, "filename": file.filename, "content_type": file.content_type, "size": size}


@router.post("/hotel/{hotel_id}/building", status_code=status.HTTP_201_CREATED)
async def upload_hotel_building_photo(hotel_id: int, file: UploadFile = File(...), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    extension = _validate_file(file)
    if extension not in IMAGE_EXTENSIONS: raise HTTPException(status_code=400, detail="Building photo must be JPG, JPEG, PNG, WEBP, or GIF.")
    hotel = db.query(Hotel).filter(Hotel.id == hotel_id).first()
    if hotel is None: raise HTTPException(status_code=404, detail="Hotel not found")
    if current_user.role == UserRole.HOTEL_OWNER and hotel.owner_id != current_user.id: raise HTTPException(status_code=404, detail="Hotel not found")
    if current_user.role not in (UserRole.HOTEL_OWNER, UserRole.ADMIN): raise HTTPException(status_code=403, detail="Hotel owner or admin access required")
    url, size = await _save_file(file, extension)
    for photo in hotel.photos:
        if photo.category == "building" and photo.photo_url.endswith("property-placeholder.svg"):
            photo.photo_url = url; photo.caption = file.filename; photo.is_primary = True; photo.sort_order = 0
            for other in hotel.photos:
                if other.id != photo.id: other.is_primary = False
            db.commit(); db.refresh(photo)
            return {"url": url, "filename": file.filename, "content_type": file.content_type, "size": size, "photo_id": photo.id}
    for other in hotel.photos: other.is_primary = False
    photo = HotelPhoto(hotel_id=hotel.id, photo_url=url, caption=file.filename, category="building", is_primary=True, sort_order=0)
    db.add(photo); db.commit(); db.refresh(photo)
    return {"url": url, "filename": file.filename, "content_type": file.content_type, "size": size, "photo_id": photo.id}


@router.post("/hotel/{hotel_id}/photo/{photo_id}", status_code=status.HTTP_201_CREATED)
async def replace_hotel_photo(hotel_id: int, photo_id: int, file: UploadFile = File(...), current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    extension = _validate_file(file)
    if extension not in IMAGE_EXTENSIONS: raise HTTPException(status_code=400, detail="Property photo must be JPG, JPEG, PNG, WEBP, or GIF.")
    photo = db.query(HotelPhoto).filter(HotelPhoto.id == photo_id, HotelPhoto.hotel_id == hotel_id).first()
    if photo is None: raise HTTPException(status_code=404, detail="Property photo not found")
    url, size = await _save_file(file, extension)
    photo.photo_url = url; photo.caption = file.filename
    if photo.category == "building" or photo.is_primary:
        for other in db.query(HotelPhoto).filter(HotelPhoto.hotel_id == hotel_id).all(): other.is_primary = other.id == photo.id
        photo.is_primary = True
    db.commit(); db.refresh(photo)
    return {"url": url, "filename": file.filename, "content_type": file.content_type, "size": size, "photo_id": photo.id}


@router.post("/hotel/{hotel_id}/document/{document_id}", status_code=status.HTTP_201_CREATED)
async def replace_hotel_document(hotel_id: int, document_id: int, file: UploadFile = File(...), current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    extension = _validate_file(file)
    document = db.query(HotelDocument).filter(HotelDocument.id == document_id, HotelDocument.hotel_id == hotel_id).first()
    if document is None: raise HTTPException(status_code=404, detail="Registration document not found")
    url, size = await _save_file(file, extension); document.document_url = url
    db.commit(); db.refresh(document)
    return {"url": url, "filename": file.filename, "content_type": file.content_type, "size": size, "document_id": document.id}


@router.post("/hotel/{hotel_id}/owner-document/{document_kind}", status_code=status.HTTP_201_CREATED)
async def replace_owner_document(hotel_id: int, document_kind: str, file: UploadFile = File(...), current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    extension = _validate_file(file)
    if document_kind not in {"cnic_front", "cnic_back", "signed_agreement"}: raise HTTPException(status_code=400, detail="Unsupported owner document type")
    hotel = db.query(Hotel).filter(Hotel.id == hotel_id).first()
    if hotel is None: raise HTTPException(status_code=404, detail="Hotel not found")
    url, size = await _save_file(file, extension)
    if document_kind == "cnic_front": hotel.owner_cnic_front_url = url
    elif document_kind == "cnic_back": hotel.owner_cnic_back_url = url
    else: hotel.signed_agreement_url = url
    db.commit(); db.refresh(hotel)
    return {"url": url, "filename": file.filename, "content_type": file.content_type, "size": size, "document_kind": document_kind}
