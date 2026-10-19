from pydantic import BaseModel, EmailStr


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