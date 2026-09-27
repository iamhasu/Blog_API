from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models.user import User
from app.schemas.post import PostResponse, PostCreate, PostUpdate
from app.dependencies.auth import get_current_user
from app.services.post import create_post, get_posts, update_post, get_user_post, delete_post, get_post_by_id





router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)

@router.post(
    "",
    response_model=PostResponse,
    status_code=201
)
def create_new_post(
    data: PostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return create_post(
        db,
        current_user.id,
        data.title,
        data.content
    )

@router.get(
    "",
    response_model=list[PostResponse]
)
def get_all_posts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_posts(db)


@router.get(
    "/{post_id}",
    response_model=PostResponse,
    status_code=200
)
def get_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_post_by_id(db, post_id)



@router.put(
    "/{post_id}",
    response_model=PostResponse
)
def update_existing_post(
    post_id: int,
    data: PostUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    post = get_user_post(
        db,
        post_id,
        current_user.id
    )

    if post is None:
        raise HTTPException(
            status_code=404,
            detail="Post not found"
        )

    return update_post(
        db,
        post,
        data.title,
        data.content
    )

@router.delete(
    "/{post_id}",
    status_code=204
)
def delete_existing_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    post = get_user_post(
        db,
        post_id,
        current_user.id
    )

    if post is None:
        raise HTTPException(
            status_code=404,
            detail="Post not found"
        )

    delete_post(db, post)

    return None

