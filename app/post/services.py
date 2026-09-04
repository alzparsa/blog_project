from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.post.models import Post, PostLike
from app.post.schemas import PostCreateRequest, PostUpdateRequest


def resolveAccountId(currentAccount: Any) -> int:
    """Works whether get_current_account returns an ORM Account, a dict, or a JWT payload."""
    if isinstance(currentAccount, dict):
        for key in ("id", "accountId", "accId", "sub"):
            if currentAccount.get(key) is not None:
                return int(currentAccount[key])
    for attr in ("id", "accountId", "accId"):
        value = getattr(currentAccount, attr, None)
        if value is not None:
            return int(value)
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not resolve account from token.",
    )


def assertIdentity(tokenAccountId: int, claimedAccId: int) -> None:
    """Stops account A from posting as account B."""
    if int(tokenAccountId) != int(claimedAccId):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="accId does not match the authenticated account.",
        )


def getPostOr404(db: Session, postId: int) -> Post:
    post = db.query(Post).filter(Post.postId == postId).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found.")
    return post


def createPost(db: Session, payload: PostCreateRequest, tokenAccountId: int) -> Post:
    assertIdentity(tokenAccountId, payload.accId)

    post = Post(
        header=payload.header.strip(),
        body=payload.body,
        attachment=payload.attachment,
        accountId=payload.accId,
        likes=0,
    )
    db.add(post)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Could not create post."
        )
    db.refresh(post)
    return post


def updatePost(db: Session, payload: PostUpdateRequest, tokenAccountId: int) -> Post:
    assertIdentity(tokenAccountId, payload.accId)
    post = getPostOr404(db, payload.postId)

    if int(post.accountId) != int(tokenAccountId):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You can only edit your own posts."
        )

    data = payload.model_dump(exclude_unset=True, exclude={"postId", "accId"})
    if not data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update."
        )

    if "header" in data and data["header"] is not None:
        data["header"] = data["header"].strip()

    for field, value in data.items():
        setattr(post, field, value)

    db.commit()
    db.refresh(post)
    return post


def toggleLike(db: Session, postId: int, tokenAccountId: int) -> tuple[Post, bool]:
    """Returns (post, liked). Idempotent per account: like → unlike → like."""
    post = getPostOr404(db, postId)

    existing = (
        db.query(PostLike)
        .filter(PostLike.postId == postId, PostLike.accountId == tokenAccountId)
        .first()
    )

    if existing:
        db.delete(existing)
        post.likes = max(0, (post.likes or 0) - 1)
        liked = False
    else:
        db.add(PostLike(postId=postId, accountId=tokenAccountId))
        post.likes = (post.likes or 0) + 1
        liked = True

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Like state changed, retry."
        )

    db.refresh(post)
    return post, liked
