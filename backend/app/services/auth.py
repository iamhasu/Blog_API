import secrets
from datetime import datetime, timedelta, timezone
from argon2 import PasswordHasher
from sqlalchemy import select
from sqlalchemy.orm import Session
from argon2.exceptions import VerifyMismatchError

from app.database.models.user import User
from app.database.models.session import SessionModel

password_hasher = PasswordHasher()

def get_user_by_email(
        db:Session,
        email: str
):

    statement = select(User).where(User.email == email)

    result = db.execute(statement)

    return result.scalar_one_or_none()

def register_user(
        db: Session,
        email: str,
        password: str
):

    existing_user = get_user_by_email(db, email)\

    if existing_user:
        return None

    password_hash = password_hasher.hash(password)

    user = User(
        email=email,
        password_hash=password_hash
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user

def authenticated_user(
        db: Session,
        email: str,
        password: str
):
    user = get_user_by_email(db, email)

    if user is None:
        return None

    try:
        password_hasher.verify(user.password_hash, password)
    except VerifyMismatchError:
        return None

    return user




SESSION_DURATION = timedelta(minutes=30)


def create_session(db: Session, user_id: int):
    session_id = secrets.token_urlsafe(32)

    expires_at = (
        datetime.now(timezone.utc)
        + SESSION_DURATION
    )

    session = SessionModel(
        id=session_id,
        user_id=user_id,
        expires_at=expires_at
    )

    db.add(session)
    db.commit()

    return session


def delete_session(
        db: Session,
        session_id: str
):
    session = db.get(SessionModel, session_id)

    if session is not None:
        db.delete(session)
        db.commit()


