# users.py
import uuid
from typing import Optional
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin, models 
from fastapi_users.authentication import(
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy
)
from fastapi_users.db import SQLAlchemyUserDatabase
from src.db import User, get_user_db
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
load_dotenv()

SECRET = os.getenv("JWT_SECRET")


# JWT_SECRET = "....."
# openssl rand -hex 32

# or you can use python to generate a random secret key
# python -c "import secrets; print(secrets.token_hex(32))"

class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")

    async def on_after_request_verify(self, user: User, token: str, request: Optional[Request] = None):
        print(f"Verification requested for user {user.id}. Verification token: {token}")

async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)

bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")

def get_jwt_strategy() :
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600) # 1hr expiration time for the token ,theres is default value for lifetime_seconds in JWTStrategy, but we can override it here, more time means less security, less time means more security but also less convenience for the user, so you need to find a balance between security and convenience.

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy
)

fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager=get_user_manager,
    auth_backends=[auth_backend]
) #

current_active_user = fastapi_users.current_user(active=True) 

# after this setup, All JWT related routes are automatically created for us, such as /auth/jwt/login, /auth/jwt/logout, /auth/jwt/refresh, /auth/jwt/verify, etc. We can also create our own custom routes if we want to, but these are the basic routes that are needed for JWT authentication.

