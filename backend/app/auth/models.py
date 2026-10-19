from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base

class Token(Base):
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    accountId = Column(Integer, ForeignKey("accounts.id"), nullable=False, index=True)
    refreshToken = Column(String, nullable=False)
    isActive = Column(Boolean, default=True, nullable=False)
    createdAt = Column(DateTime(timezone=True), server_default=func.now())
    updatedAt = Column(DateTime(timezone=True), onupdate=func.now())


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    accountId = Column(Integer, ForeignKey("accounts.id"), nullable=False, index=True)

    token = Column(String, unique=True, nullable=False, index=True)
    expiresAt = Column(DateTime(timezone=True), nullable=False)
    isRevoked = Column(Boolean, default=False, nullable=False)

    createdAt = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
