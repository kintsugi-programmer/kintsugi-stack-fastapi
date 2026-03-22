# Authenticated REST API with FastAPI, OAuth2, and JSON Web Tokens

- res: https://www.youtube.com/watch?v=KxR3OONvDvo

---

## Overview

This guide covers building a secure, authenticated REST API using **FastAPI**, **OAuth2**, and **JSON Web Tokens (JWT)**. It extends a basic API structure that already has endpoints, models, and a database configured. The focus here is adding an authentication layer.

---

## Prerequisites & Installation

Install all required packages using pip:

```bash
pip3 install fastapi
pip3 install sqlalchemy
pip3 install pydantic
pip3 install uvicorn
pip3 install passlib
```

- **FastAPI** — the web framework
- **SQLAlchemy** — ORM for database interaction
- **Pydantic** — data validation and API models
- **Uvicorn** — ASGI server used to run FastAPI (lighter than Flask's built-in server)
- **Passlib** — password hashing library (provides bcrypt support)

### Running the FastAPI Server

```bash
uvicorn my_api:app --reload
```

- Replace `my_api` with the name of your Python file
- `--reload` enables auto-reload on file changes
- Access the **Swagger UI** docs at: `http://127.0.0.1:8000/docs`

---

## Imports

```python
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from typing import Optional
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
```

- `CryptContext` — used to hash and verify passwords with bcrypt
- `OAuth2PasswordBearer` — provides token-based bearer authentication
- `OAuth2PasswordRequestForm` — handles login form data (username + password)
- `jwt` — encodes and decodes JSON Web Tokens
- `Optional` — type hint for optional fields that can be `None`
- `datetime`, `timedelta` — used to set token expiration times

---

## Security Configuration

These are constant variables required by OAuth2 and JWT:

```python
SECRET_KEY = "codewithjosh"          # In production, keep this private/secret
ALGORITHM = "HS256"                  # Hashing algorithm for JWT
TOKEN_EXPIRES = 30                   # Token validity in minutes (default: 30)
```

> **Note:** In a production environment, `SECRET_KEY` must be stored as a private environment variable — never hardcoded.

---

## Password Hashing Setup

```python
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
```

- Uses **bcrypt** as the hashing scheme
- `deprecated="auto"` acts as a safety net for older hashing schemes

---

## OAuth2 Bearer Setup

```python
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
```

- Tells FastAPI where to retrieve the token (the `/token` endpoint)
- The **bearer token** is what gets returned to the client after successful login

---

## Database Models (SQLAlchemy)

Two new columns are added to the existing `User` database model:

```python
from sqlalchemy import Boolean

# New additions to User model
hashed_password = Column(String, nullable=False)   # Stores the bcrypt hash; cannot be empty
is_active = Column(Boolean, default=True)          # Tracks if user is active; defaults to True
```

- `nullable=False` ensures the password field is never empty in the database
- `is_active` determines whether a logged-in user can access protected endpoints

---

## Pydantic API Models

There are five Pydantic models used to interact with the API:

### 1. `UserCreate` — for creating a user

```python
class UserCreate(BaseModel):
    name: str
    email: str
    role: str
    password: str
```

### 2. `UserResponse` — for returning user data (hides password)

```python
class UserResponse(BaseModel):
    name: str
    email: str
    role: str
    is_active: bool
```

- Used after a user is created to prevent exposing the password
- Overlaps the existing model and hides private details

### 3. `UserLogin` — for logging in

```python
class UserLogin(BaseModel):
    email: str
    password: str
```

### 4. `Token` — the token returned on successful login

```python
class Token(BaseModel):
    access_token: str
    token_type: str
```

### 5. `TokenData` — the data embedded in the token

```python
class TokenData(BaseModel):
    email: Optional[str] = None
```

- `email` is optional — if not provided, defaults to `None`
- Links the token to the authenticated user's email

---

## Helper / Security Functions

### Verify Password

Checks if the plain password matches the stored hashed password.

```python
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_context.verify(plain_password, hashed_password)
```

- Returns `True` if they match, `False` otherwise

### Get Password Hash

Hashes a plain-text password using bcrypt.

```python
def get_password_hash(password: str) -> str:
    return password_context.hash(password)
```

- Returns a bcrypt hash string (a jumbled, irreversible version of the password)

### Create Access Token

Encodes user data and expiry time into a JWT.

```python
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
```

- Takes a dictionary `data` (containing the subject/user info) and an optional expiry
- If no expiry is provided, defaults to **15 minutes** as a safety net
- Encodes using `SECRET_KEY` and `ALGORITHM`
- Returns the encoded JWT string

### Verify Token

Decodes and validates a JWT; raises an error if invalid.

```python
def verify_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not verify credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return TokenData(email=email)
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not verify credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
```

- Decodes the JWT using the secret key and algorithm
- Extracts the `sub` (subject) field which holds the user's email
- Raises a `401 Unauthorized` error if the email is missing or the token is invalid
- **Purpose:** Prevents a logged-in user from performing destructive actions using an invalid token (e.g., deleting their own account and locking themselves out)

---

## OAuth2 Dependency Functions

### `get_current_user`

Retrieves the currently logged-in user based on the token.

```python
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    token_data = verify_token(token)
    user = db.query(User).filter(User.email == token_data.email).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User does not exist")
    return user
```

- `Depends(oauth2_scheme)` — requires a valid bearer token to proceed
- `Depends(get_db)` — requires a working database session
- Queries the database by the email from the token
- Returns the user if found, otherwise raises a `404` error

### `get_current_active_user`

Ensures the current user is active (not deactivated).

```python
def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=404, detail="Inactive user")
    return current_user
```

- Depends on `get_current_user` — both must pass for this function to run
- If the user is not active, raises a `404` error with the message "Inactive user"

---

## Authentication Endpoints

### Register a New User

```python
@app.post("/register", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already created")
    
    hashed_password = get_password_hash(user.password)
    db_user = User(
        name=user.name,
        email=user.email,
        role=user.role,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
```

- Checks if the email already exists; raises an error if it does
- Hashes the password before saving
- Commits the new user to the database and returns their data using `UserResponse` (password hidden)

### Login and Get Access Token

```python
@app.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Wrong info")
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    access_token_expires = timedelta(minutes=TOKEN_EXPIRES)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
```

- Takes login credentials via `OAuth2PasswordRequestForm` (username = email, password)
- Verifies user exists and password matches
- Checks the user is active
- Generates a JWT valid for 30 minutes
- Returns the token and token type (`bearer`)

---

## Protected Endpoints

All protected endpoints use `Depends(get_current_active_user)` to enforce authentication.

### Get Profile

```python
@app.get("/profile", response_model=UserResponse)
def get_profile(current_user: User = Depends(get_current_active_user)):
    return current_user
```

### Verify Token Endpoint

```python
@app.get("/verify-token")
def verify_token_endpoint(current_user: User = Depends(get_current_active_user)):
    return current_user
```

### Get All Users (Protected)

```python
@app.get("/users")
def get_users(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    # returns all users
```

### Get Single User (Protected)

```python
@app.get("/users/{user_id}")
def get_user(user_id: int, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    # returns user by ID
```

### Create User (Protected)

When creating a user through a protected endpoint, the password must be hashed:

```python
hashed_password = get_password_hash(user.password)
db_user = User(
    name=user.name,
    email=user.email,
    role=user.role,
    hashed_password=hashed_password
)
```

### Update User (Protected)

```python
db_user.name = update_user.name
db_user.email = update_user.email
db_user.role = update_user.role
db.commit()
```

### Delete User (Protected, with Self-Delete Prevention)

```python
@app.delete("/users/{user_id}")
def delete_user(user_id: int, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    # proceed with deletion
```

- **Safety net:** A logged-in user cannot delete their own account, which would lock them out of the API

---

## How the Full Auth Flow Works

1. **Register** — User submits name, email, role, and password via `/register`. Password is hashed and stored.
2. **Login** — User submits email and password to `/token`. If valid, a JWT is returned.
3. **Authorize** — User pastes the JWT into the Swagger UI authorization field (or sends it as a Bearer token in the `Authorization` header).
4. **Access Protected Endpoints** — All protected routes check the token via `Depends(get_current_active_user)` before allowing access.
5. **Token Expiry** — The token is valid for 30 minutes. After expiry, the user must log in again.
6. **Logout** — In Swagger UI, clicking "Logout" removes the token. Without a valid token, all protected endpoints return `401 Unauthorized`.

---

## Common Errors and Fixes

| Error | Cause | Fix |
|---|---|---|
| `Internal Server Error` on user creation | Password field added to Pydantic model but not handled in endpoint | Ensure `get_password_hash` is called before saving |
| SQL cross errors on restart | Schema mismatch with existing database | Delete the database file and restart the server to regenerate it |
| `422 Unprocessable Entity` | Missing required field in request body | Check all required Pydantic fields are included in the request |
| `401 Unauthorized` | No token provided or token expired | Log in again via `/token` to get a new token |
| `404 User does not exist` | Token email does not match any database record | Re-register or verify the correct credentials are used |

---

## Key Concepts Summary

- **JWT (JSON Web Token)** — A compact, encoded token that carries user identity and expiry info. Used to authenticate subsequent requests after login.
- **OAuth2** — The authorization framework used to issue and validate bearer tokens.
- **Bearer Token** — The token itself. Whoever holds it ("bears" it) is considered authenticated.
- **bcrypt** — A password hashing algorithm that turns a plain password into an irreversible hash. `passlib` provides the interface for bcrypt in Python.
- **Hashing** — A one-way function that converts a password into a fixed-length string of characters. The original password cannot be recovered from the hash.
- **`Depends()`** — FastAPI's dependency injection system. Ensures a function only runs if its dependencies (e.g., valid token, active database) are satisfied first.
- **`response_model`** — Controls which fields FastAPI returns in the response. Used with `UserResponse` to hide the password from API responses.