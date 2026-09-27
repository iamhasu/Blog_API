from pydantic import BaseModel
from datetime import datetime


class PostCreate(BaseModel):
    title: str
    content: str


class PostResponse(BaseModel):
    id: int
    user_id: int
    title: str
    content: str
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes":True
    }


class PostUpdate(BaseModel):
    title: str
    content:str