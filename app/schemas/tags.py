# app/schemas/tags.py
from pydantic import BaseModel, Field, EmailStr

class Tag(BaseModel):
    tags_name: str = Field(..., example="travel")

class TagCreate(Tag):
    pass

class TagResponse(Tag):
    tags_id: int = Field(..., example=1)

    class Config:
        from_attributes = True