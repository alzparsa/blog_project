from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth.schemas import (
    CreateAccountRequest,
    CreateAccountResponse,
    UpdateAccountRequest,
    UpdateAccountResponse,
    CreateAccessTokenRequest,
    CreateAccessTokenResponse,
    CreateRefreshTokenRequest,
    CreateRefreshTokenResponse,
)
from app.auth.services import (
    create_account as create_account_service,
    get_account as get_account_service,
    update_account as update_account_service,
    delete_account as delete_account_service,
    create_access_token_service,
    refresh_access_token_service,
    get_current_account
)


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/accounts", response_model=CreateAccountResponse, status_code=201)
def create_account(payload: CreateAccountRequest, db: Session = Depends(get_db)):
    return create_account_service(payload, db)


@router.get("/accounts/{account_id}", response_model=CreateAccountResponse)
def get_account(account_id: int, db: Session = Depends(get_db)):
    return get_account_service(account_id, db)


@router.put("/accounts/{account_id}", response_model=UpdateAccountResponse)
def update_account(account_id: int, payload: UpdateAccountRequest, db: Session = Depends(get_db), current_account: dict = Depends(get_current_account)):
    return update_account_service(account_id, payload, db, authenticated_account_id=current_account["account_id"])


@router.delete("/accounts/{account_id}", status_code=204)
def delete_account(account_id: int, db: Session = Depends(get_db)):
    return delete_account_service(account_id, db)


@router.post("/login",response_model=CreateAccessTokenResponse)
def access_token(payload: CreateAccessTokenRequest, db: Session = Depends(get_db)):
    return create_access_token_service(db=db, account_id=payload.accountId, email=payload.email, password=payload.password)

@router.post("/refresh-token", response_model=CreateRefreshTokenResponse)
def refresh_token(payload: CreateRefreshTokenRequest):
    return refresh_access_token_service(
        refresh_token=payload.refreshToken,
    )
