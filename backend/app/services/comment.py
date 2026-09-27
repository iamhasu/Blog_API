from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models.comment import Comment
from app.database.models.post import Post

def create_comment(
        db: Session,
        user_id: int,
        post_id: int,
        content: str
):
    statement = select(Post).where(
        Post.id==post_id
    )

    result = db.execute(statement)

    post = result.scalar_one_or_none()

    if post is None:
        return None

    comment = Comment(
        user_id=user_id,
        post_id=post_id,
        content=content
    )

    db.add(comment)
    db.commit()
    db.refresh(comment)

    return comment

def get_comments(
    db: Session,
    post_id: int
):
    post = db.get(Post, post_id)

    if post is None:
        return None
    
    statement = (
        select(Comment)
        .where(Comment.post_id == post_id)
        .order_by(Comment.created_at.desc())
    )

    result = db.execute(statement)

    return result.scalars().all()


def delete_comment(
    db: Session,
    comment_id: int,
    user_id: int
):
    comment = db.get(Comment, comment_id)

    if comment is None:
        return "not_found"

    if comment.user_id != user_id:
        return "forbidden"

    db.delete(comment)
    db.commit()

    return "deleted"