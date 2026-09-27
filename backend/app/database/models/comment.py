from datetime import datetime, timezone

from sqlalchemy import ForeignKey, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base

class Comment(Base):
    __tablename__="comments"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    post_id: Mapped[int] = mapped_column(
    ForeignKey("posts.id"),
    nullable=False
)

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )