from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.services import get_current_account  # adjust if it lives in dependencies.py
from app.post import services
from app.post.schemas import (
    LikeRequest,
    LikeResponse,
    PostCreateRequest,
    PostResponse,
    PostUpdateRequest,
)

router = APIRouter(prefix="/posts", tags=["Posts"])


@router.post("", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def createPost(
    payload: PostCreateRequest,
    db: Session = Depends(get_db),
    currentAccount=Depends(get_current_account),
):
    accountId = services.resolveAccountId(currentAccount)
    post = services.createPost(db, payload, accountId)
    return PostResponse(
        postId=post.postId, responseCode=201, responseMessage="Post created successfully."
    )


@router.patch("", response_model=PostResponse)
def patchPost(
    payload: PostUpdateRequest,
    db: Session = Depends(get_db),
    currentAccount=Depends(get_current_account),
):
    accountId = services.resolveAccountId(currentAccount)
    post = services.updatePost(db, payload, accountId)
    return PostResponse(
        postId=post.postId, responseCode=200, responseMessage="Post updated successfully."
    )


@router.put("/like", response_model=LikeResponse)
def putLike(
    payload: LikeRequest,
    db: Session = Depends(get_db),
    currentAccount=Depends(get_current_account),
):
    accountId = services.resolveAccountId(currentAccount)
    post, liked = services.toggleLike(db, payload.postId, accountId)
    return LikeResponse(
        postId=post.postId,
        likes=post.likes,
        liked=liked,
        responseCode=200,
        responseMessage="Post liked." if liked else "Like removed.",
    )

@router.get("/debug/whoami")
def whoami(current_account = Depends(get_current_account)):
    return {
        "type": str(type(current_account)),
        "repr": repr(current_account)[:500],
        "attrs": [a for a in dir(current_account) if not a.startswith("_")][:60],
    }