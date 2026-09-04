# app/auth/services.py
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from app.auth import models, schemas
from datetime import datetime, timedelta, timezone
from jose import jwt,JWTError
from os import getenv
import os
from app.config import SECRET_KEY, ALGORITHM

security = HTTPBearer()

# Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ACCESS_TOKEN_EXPIRE_MINUTES = 5
REFRESH_TOKEN_EXPIRE_HOURS = 1


def get_current_account(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    token = credentials.credentials

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        account_id = payload.get("sub")
        email = payload.get("email")
        token_type = payload.get("token_type")

        if account_id is None or email is None:
            raise credentials_exception

        if token_type != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="An access token is required",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return {
            "account_id": int(account_id),
            "email": email,
        }

    except (JWTError, ValueError):
        raise credentials_exception

    
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



def delete_account(account_id: int, db: Session):
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

def create_access_token(
    data: dict,
    expires_delta: timedelta,
) -> str:
    payload = data.copy()

    expire = datetime.now(timezone.utc) + expires_delta
    payload["exp"] = expire

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

def create_refresh_token(
    data: dict,
    expires_delta: timedelta,
) -> str:
    payload = data.copy()

    expire = datetime.now(timezone.utc) + expires_delta
    payload["exp"] = expire

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

def create_access_token_service(
    db: Session,
    account_id: int,
    email: str,
    password: str,
) -> dict:
    # 1. Validate required values
    if account_id is None or not email or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="accountId, email, and password are required",
        )

    # 2. Find the account by email
    account = (
        db.query(models.Account)
        .filter(models.Account.email == email)
        .first()
    )

    if account is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    # 3. Verify that the account ID matches the email
    if account.id != account_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    # 4. Verify the submitted password against the stored hash
    if not pwd_context.verify(password, account.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    # 5. Activate the account after successful verification
    account.isActive = True

    # 6. Create a short-lived access token
    access_token = create_access_token(
        data={
            "sub": str(account.id),
            "email": account.email,
            "token_type": "access",
        },
        expires_delta=timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES,
        ),
    )

    # 7. Create a longer-lived refresh token
    refresh_token = create_refresh_token(
        data={
            "sub": str(account.id),
            "token_type": "refresh",
        },
        expires_delta=timedelta(
            hours=REFRESH_TOKEN_EXPIRE_HOURS,
        ),
    )

    # 8. Save isActive=True
    db.commit()
    db.refresh(account)

    # 9. Return the response expected by the schema
    return {
        "accessToken": access_token,
        "refreshToken": refresh_token,
        "responseCode": 200,
        "responseMessage": "Access token created successfully",
    }

def refresh_access_token_service(
    refresh_token: str,
) -> dict:
    try:
        payload = jwt.decode(
            refresh_token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        account_id = payload.get("sub")
        token_type = payload.get("token_type")

        if account_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )

        if token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="A refresh token is required",
            )

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    new_access_token = create_access_token(
        data={
            "sub": str(account_id),
            "token_type": "access",
        },
        expires_delta=timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES,
        ),
    )

    return {
        "accessToken": new_access_token,
        "responseCode": 200,
        "responseMessage": "Access token refreshed successfully",
    }
