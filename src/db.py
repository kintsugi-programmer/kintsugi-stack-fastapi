# db.py
from collections.abc import AsyncGenerator
from datetime import datetime
import uuid 
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, relationship
from fastapi_users.db import SQLAlchemyUserDatabase, SQLAlchemyBaseUserTableUUID
from fastapi import Depends
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
# DATABASE_URL = "sqlite+aiosqlite:///./test.db"

class Base(DeclarativeBase): # we can't directly use declarative_base() because we need to use it in async way, so we create a class that inherits from DeclarativeBase and then we can use it to create our models
    pass

# we are using SQLAlchemyBaseUserTableUUID because we want to use UUID as our primary key, and it already has the necessary fields for user management, such as email, hashed_password, is_active, is_superuser, etc.

class User(SQLAlchemyBaseUserTableUUID, Base) :
    posts  = relationship("Post", back_populates="user")


class Post(Base):
    __tablename__ = "posts"
    id = Column(UUID(as_uuid=True),primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True),ForeignKey("user.id"),nullable=False) # NEW # FK 
    caption = Column(Text)
    url = Column(String, nullable=False)
    file_type = Column(String, nullable= False)
    file_name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User",back_populates="posts") # NEW # this is the relationship that allows us to access the user from the post, and also access the posts from the user, it's a bidirectional relationship, we use back_populates to specify the name of the relationship in the other model, so that SQLAlchemy can automatically handle the relationship for us.

# One to many relationship, One User can have many posts
# if wanna flip, then make FK at User table & back_populates

engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

async def get_user_db(session: AsyncSession = Depends(get_async_session)): 
    yield SQLAlchemyUserDatabase(session, User) 
    # this is a FastAPI dependency that will allow us to get the user database for each request, it will create a new session for each request and close it after the request is done, so that we don't have any connection leaks, and we can ensure that our application is properly cleaned up when it shuts down.
