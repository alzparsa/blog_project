from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.services import get_current_account
from app.post import services
from app.post.schemas import (
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
    current_account: dict = Depends(get_current_account),
):
    post = services.createPost(db, payload, current_account["account_id"])
    return PostResponse(
        postId=post.postId, responseCode=201, responseMessage="Post created successfully."
    )


@router.patch("/{postId}", response_model=PostResponse)
def likwPost(
    postId: int,
    db: Session = Depends(get_db),
    current_account: dict = Depends(get_current_account),
):
    post = services.updatePost(postId, db, current_account["account_id"])
    return PostResponse(
        postId=post.postId, responseCode=200, responseMessage="Post updated successfully."
    )


@router.post("/{postId}/like", response_model=LikeResponse)
def putLike(
    postId: int,
    db: Session = Depends(get_db),
    current_account: dict = Depends(get_current_account),
):
    post, liked = services.toggleLike(postId, db, current_account["account_id"])
    return LikeResponse(
        postId=post.postId,
        likes=post.likes,
        liked=liked,
        responseCode=200,
        responseMessage="Post liked." if liked else "Like removed.",
    )
