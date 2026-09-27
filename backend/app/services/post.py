from sqlalchemy.orm import Session
from sqlalchemy import select

from app.database.models.post import Post

def create_post(
        db: Session,
        user_id: int,
        title: str,
        content: str
):
    post = Post(
        user_id=user_id,
        title=title,
        content=content
    )

    db.add(post)
    db.commit()
    db.refresh(post)

    return post 


def get_posts(db: Session):
    statement = select(Post)

    result = db.execute(statement)

    return result.scalars().all()


def get_user_post(
    db: Session,
    post_id: int,
    user_id: int
):
    statement = select(Post).where(
        Post.id == post_id,
        Post.user_id == user_id
    )

    result = db.execute(statement)

    return result.scalar_one_or_none()


def update_post(
    db: Session,
    post: Post,
    title: str,
    content: str
):
    post.title = title
    post.content = content

    db.commit()
    db.refresh(post)

    return post


def delete_post(
    db: Session,
    post: Post
):
    db.delete(post)
    db.commit()


def get_post_by_id(db: Session, post_id: int):
    statement = select(Post).where(
        Post.id == post_id
    )

    result = db.execute(statement)

    return result.scalar_one_or_none()