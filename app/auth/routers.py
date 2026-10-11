from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth.schemas import (
    CreateAccessTokenRequest,
    CreateAccessTokenResponse,
    CreateRefreshTokenRequest,
    CreateRefreshTokenResponse,
)
from app.auth.services import (
    create_access_token_service,
    refresh_access_token_service,
)


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=CreateAccessTokenResponse)
def access_token(payload: CreateAccessTokenRequest, db: Session = Depends(get_db)):
    return create_access_token_service(db=db, account_id=payload.accountId, email=payload.email, password=payload.password)


@router.post("/refresh-token", response_model=CreateRefreshTokenResponse)
def refresh_token(payload: CreateRefreshTokenRequest):
    return refresh_access_token_service(
        refresh_token=payload.refreshToken,
    )
