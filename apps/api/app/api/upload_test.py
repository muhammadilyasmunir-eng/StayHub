from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from sqlalchemy import text

from app.db.session import engine


router = APIRouter(prefix="/upload-test", tags=["Upload Test"])
UPLOAD_ROOT = Path("app/static/uploads/test")
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
MAX_FILE_SIZE = 10 * 1024 * 1024


def ensure_test_table() -> None:
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS upload_test_submissions (
                    id BIGSERIAL PRIMARY KEY,
                    message TEXT NOT NULL,
                    filename TEXT NOT NULL,
                    file_url TEXT NOT NULL,
                    content_type TEXT,
                    file_size BIGINT NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
                """
            )
        )


@router.post("")
async def submit_upload_test(
    message: str = Form(...),
    photo: UploadFile = File(...),
):
    message = message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="Text is required.")
    if not photo.filename:
        raise HTTPException(status_code=400, detail="Photo is required.")

    extension = Path(photo.filename).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only JPG, JPEG, PNG, WEBP and GIF photos are allowed.")

    content = await photo.read(MAX_FILE_SIZE + 1)
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="Photo is too large. Maximum size is 10 MB.")

    UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)
    safe_name = f"{uuid4().hex}{extension}"
    destination = UPLOAD_ROOT / safe_name
    destination.write_bytes(content)
    file_url = f"/static/uploads/test/{safe_name}"

    ensure_test_table()
    with engine.begin() as conn:
        result = conn.execute(
            text(
                """
                INSERT INTO upload_test_submissions
                    (message, filename, file_url, content_type, file_size)
                VALUES
                    (:message, :filename, :file_url, :content_type, :file_size)
                RETURNING id, created_at
                """
            ),
            {
                "message": message,
                "filename": photo.filename,
                "file_url": file_url,
                "content_type": photo.content_type,
                "file_size": len(content),
            },
        ).mappings().one()

    return {
        "success": True,
        "message": "Test submission successful.",
        "submission_id": result["id"],
        "text": message,
        "photo": {
            "filename": photo.filename,
            "url": file_url,
            "content_type": photo.content_type,
            "size": len(content),
        },
        "created_at": result["created_at"],
    }
