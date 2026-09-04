from pydantic import BaseModel, EmailStr, field_validator, validator, ConfigDict
from typing import Optional
from datetime import datetime


# ---------- Account Schemas ----------

class CreateAccountRequest(BaseModel):
    email: EmailStr
    password: str
    name: str
    profilePhoto: Optional[str] = None
    language: Optional[str] = "EN"

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if len(value.encode("utf-8")) > 72:
            raise ValueError("Password must be 72 bytes or fewer")
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters")
        return value


class CreateAccountResponse(BaseModel):
    id: int
    email: EmailStr
    name: str
    createdAt: datetime

    class Config:
        from_attributes = True

class UpdateAccountRequest(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    name: Optional[str] = None
    profilePhoto: Optional[str] = None
    language: Optional[str] = None

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: Optional[str]) -> Optional[str]:
        if value is not None and len(value.encode("utf-8")) > 72:
            raise ValueError("Password must be 72 bytes or fewer")
        return value



class UpdateAccountResponse(BaseModel):
    id: int
    email: EmailStr
    name: str
    updatedAt: Optional[datetime]

    class Config:
        from_attributes = True

class CreateAccessTokenRequest(BaseModel):
    accountId: int
    email: EmailStr
    password: str

class CreateAccessTokenResponse(BaseModel):
    accessToken: str
    refreshToken: str
    responseCode: int
    responseMessage: str

class CreateRefreshTokenRequest(BaseModel):
    refreshToken: str

class CreateRefreshTokenResponse(BaseModel):
    accessToken: str
    refreshToken: str | None = None
    responseCode: int
    responseMessage: str