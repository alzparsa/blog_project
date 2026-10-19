from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session
from blog_project.backend.app.database import get_db
from blog_project.backend.app.acc.schemas import (
    CreateAccountRequest,
    CreateAccountResponse,
    UpdateAccountRequest,
    UpdateAccountResponse,
    UploadProfilePhotoResponse,
)
from blog_project.backend.app.acc.services import (
    create_account as create_account_service,
    get_account as get_account_service,
    update_account as update_account_service,
    delete_account as delete_account_service,
    upload_profile_photo as upload_profile_photo_service,
)
from blog_project.backend.app.auth.services import get_current_account


# Prefix kept as "/auth" so existing endpoint URLs don't change.
router = APIRouter(prefix="/account", tags=["Accounts"])


@router.post("", response_model=CreateAccountResponse, status_code=201)
def create_account(payload: CreateAccountRequest, db: Session = Depends(get_db)):
    return create_account_service(payload, db)


@router.get("/{account_id}", response_model=CreateAccountResponse)
def get_account(account_id: int, db: Session = Depends(get_db)):
    return get_account_service(account_id, db)


@router.put("/{account_id}", response_model=UpdateAccountResponse)
def update_account(account_id: int, payload: UpdateAccountRequest, db: Session = Depends(get_db), current_account: dict = Depends(get_current_account)):
    return update_account_service(account_id, payload, db, authenticated_account_id=current_account["account_id"])


@router.delete("/{account_id}", status_code=204)
def delete_account(account_id: int, db: Session = Depends(get_db), current_account: dict = Depends(get_current_account)):
    return delete_account_service(account_id, db, authenticated_account_id=current_account["account_id"])


@router.post("/{account_id}/photo", response_model=UploadProfilePhotoResponse)
def upload_profile_photo(account_id: int, file: UploadFile = File(...), db: Session = Depends(get_db), current_account: dict = Depends(get_current_account)):
    return upload_profile_photo_service(account_id, file, db, authenticated_account_id=current_account["account_id"])
