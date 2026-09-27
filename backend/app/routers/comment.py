from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models.user import User
from app.dependencies.auth import get_current_user
from app.schemas.comment import CommentCreate, CommentResponse
from app.services.comment import create_comment, get_comments, delete_comment

router = APIRouter(
    prefix="/posts",
    tags=["Comments"]
)


@router.post(
    "/{post_id}/comments",
    response_model=CommentResponse,
    status_code=201
)
def add_comment(
    post_id: int,
    data: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    comment = create_comment(
    db=db,
    user_id=current_user.id,
    post_id=post_id,
    content=data.content
)

    if comment is None:
        raise HTTPException(
            status_code=404,
            detail="Post not found"
        )

    return comment 

@router.get(
    "/{post_id}/comments",
    response_model=list[CommentResponse]
)
def list_comments(
    post_id: int,
    db: Session = Depends(get_db)
):
    comments = get_comments(
        db=db,
        post_id=post_id
    )

    if comments is None:
        raise HTTPException(
            status_code=404,
            detail="Post not found"
        )

    return comments

@router.delete(
    "/comments/{comment_id}",
    status_code=204
)
def remove_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = delete_comment(
        db=db,
        comment_id=comment_id,
        user_id=current_user.id
    )

    if result == "not_found":
        raise HTTPException(
            status_code=404,
            detail="Comment not found"
        )

    if result == "forbidden":
        raise HTTPException(
            status_code=403,
            detail="You can only delete your own comment"
        )