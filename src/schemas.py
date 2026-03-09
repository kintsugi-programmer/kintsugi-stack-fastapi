# schemas.py
from pydantic import BaseModel # BaseModel is special Func. in Python with Special Features

class PostCreate(BaseModel):
    title: str
    content: str

class PostResponse(BaseModel):
    title: str
    content: str



