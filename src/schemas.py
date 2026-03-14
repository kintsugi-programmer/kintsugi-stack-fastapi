# schemas.py
from pydantic import BaseModel # BaseModel is special Func. in Python with Special Features
from fastapi_users import schemas
import uuid

class PostCreate(BaseModel):
    title: str
    content: str

class PostResponse(BaseModel):
    title: str
    content: str


# just for inheritance, we can use the BaseUser, BaseUserCreate, BaseUserUpdate from fastapi_users, and then we can create our own UserRead, UserCreate, UserUpdate schemas that inherit from these base schemas, so that we can use them in our API routes and also in our database models, and we can also add any additional fields that we want to these schemas if needed.
class UserRead(schemas.BaseUser[uuid.UUID]):
    pass

class UserCreate(schemas.BaseUserCreate):
    pass

class UserUpdate(schemas.BaseUserUpdate):
    pass
