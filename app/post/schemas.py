from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# ---------- Requests ----------

class PostCreateRequest(BaseModel):
    """Token comes from the Authorization header, never the body."""
    accId: int = Field(..., description="Account ID of the author")
    header: str = Field(..., min_length=1, max_length=255)
    body: str = Field(..., min_length=1)
    attachment: Optional[str] = Field(None, max_length=512)


class PostUpdateRequest(BaseModel):
    """PATCH — only send the fields that change."""
    postId: int
    accId: int
    header: Optional[str] = Field(None, min_length=1, max_length=255)
    body: Optional[str] = Field(None, min_length=1)
    attachment: Optional[str] = Field(None, max_length=512)


class LikeRequest(BaseModel):
    postId: int


# ---------- Responses ----------

class PostResponse(BaseModel):
    postId: int
    responseCode: int
    responseMessage: str


class LikeResponse(BaseModel):
    postId: int
    likes: int
    liked: bool
    responseCode: int
    responseMessage: str


class PostDetailResponse(BaseModel):
    postId: int
    header: str
    body: str
    attachment: Optional[str] = None
    likes: int
    accountId: int
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)
