from sqlalchemy import (
    Column, Integer, String, Text, DateTime, ForeignKey, UniqueConstraint, Index
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class Post(Base):
    __tablename__ = "posts"

    postId = Column(Integer, primary_key=True, index=True, autoincrement=True)
    header = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    attachment = Column(String, nullable=True)
    likes = Column(Integer, nullable=False, default=0, server_default="0")
    accountId = Column(
        Integer,
        ForeignKey("accounts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updatedAt = Column(DateTime(timezone=True), onupdate=func.now())

    account = relationship("Account", backref="posts")
    postLikes = relationship(
        "PostLike",
        back_populates="post",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    __table_args__ = (Index("ix_posts_accountId_timestamp", "accountId", "timestamp"),)


class PostLike(Base):
    """One row per (post, account) so PUT /like is an idempotent toggle."""

    __tablename__ = "post_likes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    postId = Column(
        Integer, ForeignKey("posts.postId", ondelete="CASCADE"), nullable=False, index=True
    )
    accountId = Column(
        Integer, ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    createdAt = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    post = relationship("Post", back_populates="postLikes")

    __table_args__ = (UniqueConstraint("postId", "accountId", name="uq_post_like_once"),)
