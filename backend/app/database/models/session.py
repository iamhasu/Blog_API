from datetime import datetime, timezone
from sqlalchemy import String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base

class SessionModel(Base):
    __tablename__="sessions"

    id: Mapped[str] = mapped_column(
        String(255),
        primary_key=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

