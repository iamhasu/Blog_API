from datetime import datetime, timezone, timedelta
from fastapi import Cookie, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models.session import SessionModel
from app.database.models.user import User



def get_current_user(
        session_id: str | None = Cookie(default=None),
        db:Session = Depends(get_db)
):
    if session_id is None:
        raise HTTPException(
            status_code=401,
            detail="Not aunthenticated"
        )

    statement = select(SessionModel).where(SessionModel.id == session_id)

    result = db.execute(statement)

    session = result.scalar_one_or_none()

    if session is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid session"
        )

    if session.expires_at <= datetime.now(timezone.utc):
        raise HTTPException(
            status_code=401,
            detail="Session expired"
        )

    statement = select(User).where(User.id == session.user_id)

    result = db.execute(statement)

    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )

    return user