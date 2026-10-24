# app/acc/services.py
from pathlib import Path
from uuid import uuid4
from sqlalchemy.orm import Session
from fastapi import HTTPException, UploadFile, status
from app.acc import schemas
from app.auth.services import pwd_context
from app.acc import models


def create_account(
    payload: schemas.CreateAccountRequest,
    db: Session,
):
    # 1. Check if email already exists
    existing_account = (
        db.query(models.Account)
        .filter(models.Account.email == payload.email)
        .first()
    )

    if existing_account:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # 2. Hash the password
    hashed_password = pwd_context.hash(payload.password)

    # 3. Create the new account row
    new_account = models.Account(
        email=payload.email,
        password=hashed_password,
        name=payload.name,
        profilePhoto=payload.profilePhoto,
        language=payload.language,
        isActive=False,
    )

    # 4. Save to database
    db.add(new_account)
    db.commit()
    db.refresh(new_account)

    return new_account


def get_account(account_id: int, db: Session):
    account = (
        db.query(models.Account)
        .filter(models.Account.id == account_id)
        .first()
    )

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found",
        )

    return account


def update_account(
    account_id: int,
    payload: schemas.UpdateAccountRequest,
    db: Session,
    authenticated_account_id: int
):
    if account_id != authenticated_account_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot update another account",
        )
    account = (
        db.query(models.Account)
        .filter(models.Account.id == account_id)
        .first()
    )

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found",
        )

    if payload.email is not None:
        account.email = payload.email

    if payload.password is not None:
        account.password = pwd_context.hash(payload.password)

    if payload.name is not None:
        account.name = payload.name

    if payload.profilePhoto is not None:
        account.profilePhoto = payload.profilePhoto

    if payload.language is not None:
        account.language = payload.language

    db.commit()
    db.refresh(account)

    return account


def delete_account(account_id: int, db: Session, authenticated_account_id: int):
    if account_id != authenticated_account_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot delete another account",
        )
    account = (
        db.query(models.Account)
        .filter(models.Account.id == account_id)
        .first()
    )

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found",
        )

    db.delete(account)
    db.commit()


# ---------- Profile photo upload ----------

UPLOAD_DIR = Path("uploads") / "profile_photos"
UPLOAD_URL_PREFIX = "/uploads/profile_photos"
MAX_PHOTO_BYTES = 5 * 1024 * 1024  # 5 MB

# content type -> (file extension, magic-byte check)
ALLOWED_PHOTO_TYPES = {
    "image/jpeg": (".jpg", lambda b: b.startswith(b"\xff\xd8\xff")),
    "image/png": (".png", lambda b: b.startswith(b"\x89PNG\r\n\x1a\n")),
    "image/webp": (".webp", lambda b: b[:4] == b"RIFF" and b[8:12] == b"WEBP"),
}


def upload_profile_photo(
    account_id: int,
    file: UploadFile,
    db: Session,
    authenticated_account_id: int,
):
    if account_id != authenticated_account_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot update another account",
        )

    rule = ALLOWED_PHOTO_TYPES.get(file.content_type)
    if rule is None:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only JPEG, PNG or WebP images are allowed",
        )
    extension, has_valid_signature = rule

    # Read one byte past the limit so oversized files are detected without loading them fully
    data = file.file.read(MAX_PHOTO_BYTES + 1)
    if len(data) > MAX_PHOTO_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Image must be 5 MB or smaller",
        )
    if not has_valid_signature(data):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File content does not match an image of the declared type",
        )

    account = (
        db.query(models.Account)
        .filter(models.Account.id == account_id)
        .first()
    )
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found",
        )

    # Server-generated filename: never trust the client's name
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"{account_id}_{uuid4().hex}{extension}"
    (UPLOAD_DIR / filename).write_bytes(data)

    # Remove the previous photo if it was one of our uploads
    old = account.profilePhoto
    if old and old.startswith(UPLOAD_URL_PREFIX + "/"):
        (UPLOAD_DIR / Path(old).name).unlink(missing_ok=True)

    account.profilePhoto = f"{UPLOAD_URL_PREFIX}/{filename}"
    db.commit()
    db.refresh(account)

    return account
