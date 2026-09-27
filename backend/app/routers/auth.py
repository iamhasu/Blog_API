import os

from fastapi import APIRouter, Depends, HTTPException, Response, Cookie
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.auth import RegisterRequest, LoginRequest
from app.services.auth import register_user, authenticated_user, create_session, delete_session


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/register", status_code=201)
def register(
    data: RegisterRequest,
    db: Session = Depends(get_db)
):
    user = register_user(
        db,
        data.email,
        data.password
    )

    if user is None:
        raise HTTPException(
            status_code=409,
            detail="email already registered"
        )

    return {
        "id": user.id,
        "email": user.email
    }


@router.post("/login")
def login(
    data: LoginRequest,
    response: Response,
    db: Session = Depends(get_db)
):
    user = authenticated_user(
        db,
        data.email,
        data.password
    )

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    session = create_session(
        db,
        user.id
    )

    response.set_cookie(
        key="session_id",
        value=session.id,
        httponly=True,
        secure=os.getenv("COOKIE_SECURE", "false").lower() == "true",
        samesite="lax",
        max_age=1800
    )

    return {
        "message": "Login successful"
    }

@router.post("/logout")
def logout(
    response: Response,
    session_id: str | None = Cookie(default=None),
    db:Session = Depends(get_db)
):
    if session_id is not None:
        delete_session(db, session_id)

    response.delete_cookie(
        key="session_id"
    )

    return {
        "message":  "Logout successful"
    }