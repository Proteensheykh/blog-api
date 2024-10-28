from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List
from typing_extensions import Literal


class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True

class PostCreate(PostBase):
    pass

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class UserOut(UserBase):
    id: int
    email: EmailStr

    class Config:
        from_attributes = True

class Post(PostBase):
    id: int
    owner_id: int
    owner: UserOut
    created_at: datetime

    class Config:
        orm_mode = True

class PostOut(BaseModel):
    Post: Post
    likes: int

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[int] = None    

class Like(BaseModel):
    post_id: int
    dir: Literal[0, 1] = 1
