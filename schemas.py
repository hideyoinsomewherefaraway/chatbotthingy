from typing import List, Optional
from pydantic import BaseModel


class ItemBase(BaseModel):
    title: str
    description: Optional[str] = None


class ItemCreate(ItemBase):
    pass


class Item(ItemBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool
    items: List[Item] = []

    class Config:
        from_attributes = True

class MessageBase(BaseModel):
    content: str
    is_stupid_question: bool
    role: str

class MessageCreate(MessageBase):
    pass

class Message(MessageBase):
    mId: int

    class Config:
        from_attributes = True
