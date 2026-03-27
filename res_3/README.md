# FastAPI SQL Integration: CRUD API with SQLAlchemy, SQLite & Pydantic

- res: https://www.youtube.com/watch?v=xq1Snezb1rs

---

## Overview

This guide covers how to integrate a **SQL database** into a **FastAPI** application using **SQLAlchemy** as the ORM (Object Relational Mapper). It walks through:

- Setting up a SQLite database with SQLAlchemy
- Creating database models
- Creating Pydantic models for API interaction
- Building full **CRUD** endpoints
- Testing endpoints using FastAPI's built-in documentation

> **Prerequisite:** Understanding of basic FastAPI concepts and endpoints before proceeding with SQL integration.

---

## CRUD Operations — HTTP Method Mapping

| Operation | HTTP Method | Description |
|-----------|-------------|-------------|
| **Create** | `POST` | Add new data |
| **Read** | `GET` | Fetch existing data |
| **Update** | `PUT` | Modify existing data |
| **Delete** | `DELETE` | Remove existing data |

---

## Installation

Install the following packages if not already present:

```bash
pip install fastapi
pip install sqlalchemy
pip install uvicorn
```

- **FastAPI** — the web framework
- **SQLAlchemy** — the ORM for database interaction
- **Uvicorn** — lightweight ASGI server required to run FastAPI (FastAPI is lighter than Flask and needs Uvicorn to run)

---

## Running the App

```bash
uvicorn my_api:app --reload
```

- Replace `my_api` with your filename (without `.py`)
- `app` is the FastAPI instance name
- `--reload` enables auto-reload on code changes
- Uvicorn provides a local URL to access the running app

---

## FastAPI Docs (Built-in Testing UI)

- Navigate to `http://127.0.0.1:8000/docs` after running the app
- Every endpoint defined in the app appears here automatically
- Allows interactive testing of each endpoint directly in the browser (try it out → execute)

---

## Imports

```python
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from typing import Optional, List
```

### Import Explanations

- **`FastAPI`** — main class to create the app instance
- **`HTTPException`** — used to raise HTTP errors (e.g., 404)
- **`Depends`** — declares endpoint dependencies (e.g., database session)
- **`create_engine`** — establishes the database connection
- **`Column, Integer, String`** — data types used to define database columns
- **`declarative_base`** — base class for building SQLAlchemy database models
- **`sessionmaker`** — creates database session instances
- **`Session`** — type annotation for the database session
- **`BaseModel`** — Pydantic's base class for creating API models
- **`Optional, List`** — Python typing utilities for type hints

---

## App Initialization

```python
app = FastAPI(title="Integration with SQL - Code with Josh")
```

---

## Basic Root Endpoint (Sanity Check)

```python
@app.get("/")
def root():
    return {"message": "Intro to FastAPI with SQL - Subscribe"}
```

- The `/` endpoint is the landing page
- All endpoints start with `/`
- Endpoints like `/users` or `/users/1` are built on top of this base

---

## Database Setup

### 1. Create the Engine

```python
DATABASE_URL = "sqlite:///./users.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
```

- **SQLite** is used here (simplest for development)
- Database file is named `users.db` — can be named anything as long as it ends in `.db`
- **`check_same_thread: False`** — required because FastAPI runs multiple threads and SQLite by default only allows single-thread access

### 2. Create the Session

```python
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

- **`autocommit=False`** — prevents automatic committing; changes must be committed manually
- **`autoflush=False`** — prevents automatic flushing/reloading on every operation
- **`bind=engine`** — links the session to the engine

### 3. Declare the Base

```python
Base = declarative_base()
```

- `Base` is the parent class from which all database models inherit
- Required by SQLAlchemy to manage model metadata

---

## Database Model

> A database is like an Excel spreadsheet — it has **tables**, and each table has **rows** and **columns**. A database model represents a **row** in a table.

```python
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String, unique=True, nullable=False)
    role = Column(String, nullable=True)
```

### Column Explanations

| Column | Type | Notes |
|--------|------|-------|
| `id` | `Integer` | Primary key; auto-increments; uniquely identifies each user |
| `name` | `String(100)` | Max 100 characters; cannot be empty (`nullable=False`) |
| `email` | `String` | Must be unique across all users; cannot be empty |
| `role` | `String` | Optional field (`nullable=True`) |

- **`primary_key=True`** — designates `id` as the unique identifier; automatically increments
- **`index=True`** — makes the column indexable for faster queries
- **`unique=True`** — enforces uniqueness at the database level
- **`nullable=False`** — column cannot be empty/null

### Create All Tables

```python
Base.metadata.create_all(bind=engine)
```

- Links the model to the engine and creates the actual database tables
- Must be called after defining the model

---

## Pydantic Models (API Models)

Pydantic models define the **shape of data** sent to and received from the API. They act like data classes with type validation.

### Model 1: UserCreate (Input Model)

```python
class UserCreate(BaseModel):
    name: str
    email: str
    role: str
```

- Used when **creating** a new user via POST request
- Represents the data the client sends to the API

### Model 2: UserResponse (Output Model)

```python
class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str

    class Config:
        from_attributes = True
```

- Used to **control what data is returned** from the API
- Acts as a **safety net** — prevents private/sensitive fields (e.g., password hashes, internal notes) from being exposed through the API
- **`from_attributes = True`** — required configuration so Pydantic can read data from SQLAlchemy model instances (ORM objects)

---

## Database Dependency (get_db)

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

- Creates a new database session for each request
- **`yield db`** — provides the session to the endpoint
- **`db.close()`** — ensures the session is always closed after the request, regardless of success or failure
- Used with `Depends(get_db)` inside endpoints

---

## CRUD Endpoints

### 1. GET — Get a Single User

```python
@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

- **Endpoint:** `/users/{user_id}` — `user_id` is a path parameter (e.g., `/users/1`)
- **`response_model=UserResponse`** — formats the output using the Pydantic response model
- **`db: Session = Depends(get_db)`** — injects the database session via dependency injection
- Queries the `User` table filtered by the provided `user_id`
- If no user found, raises a `404 HTTPException`
- Otherwise returns the user object

> **Common mistake:** Using `user` as both a variable name and the model name causes a `cannot access local variable` error. Use `user_id` consistently.

---

### 2. POST — Create a New User

```python
@app.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    new_user = User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
```

- **Endpoint:** `/users/`
- Accepts a `UserCreate` Pydantic model as the request body
- **Pre-check:** Queries the database to see if the email already exists before inserting
  - Email must be unique — if duplicate, raises `400` exception with detail `"User already exists"`
- **`User(**user.dict())`** — creates a new SQLAlchemy `User` object from the Pydantic model's dictionary
- **`db.add(new_user)`** — stages the new user for insertion
- **`db.commit()`** — *must be called* to persist the change; without this, Python does not send data to the database
- **`db.refresh(new_user)`** — refreshes the object with the latest state from the database (e.g., auto-generated `id`)
- Returns the newly created user

---

### 3. PUT — Update an Existing User

```python
@app.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User does not exist")

    for field, value in user.dict().items():
        setattr(db_user, field, value)

    db.commit()
    db.refresh(db_user)
    return db_user
```

- **Endpoint:** `/users/{user_id}`
- Accepts both the `user_id` path parameter and a `UserCreate` body for the new data
- **Pre-check:** Verifies the user exists; raises `404` if not found
- **`for field, value in user.dict().items()`** — iterates over all fields in the update payload
- **`setattr(db_user, field, value)`** — dynamically sets each field on the database object
- Commits and refreshes after changes
- Returns the updated user

---

### 4. DELETE — Delete a User

```python
@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User does not exist")

    db.delete(db_user)
    db.commit()
    return {"message": "User deleted"}
```

- **Endpoint:** `/users/{user_id}`
- Pre-checks existence of user before deletion
- **`db.delete(db_user)`** — marks the user for deletion
- **`db.commit()`** — persists the deletion
- **Important:** Do not attempt to `db.refresh()` or `return` the deleted user object after deletion — the object no longer exists in the session, which causes an `instance is not persistent` SQLAlchemy error
- Return a confirmation message instead

---

### 5. GET — Get All Users

```python
@app.get("/users/", response_model=List[UserResponse])
def get_all_users(db: Session = Depends(get_db)):
    return db.query(User).all()
```

- **Endpoint:** `/users/`
- **`response_model=List[UserResponse]`** — specifies the response is a list of `UserResponse` objects
- **`db.query(User).all()`** — fetches all records from the `User` table
- Does not require any path parameters — only needs the database session

---

## Key Rules for Database Operations

| Action | Required Steps |
|--------|---------------|
| Add a record | `db.add()` → `db.commit()` → `db.refresh()` |
| Update a record | modify fields → `db.commit()` → `db.refresh()` |
| Delete a record | `db.delete()` → `db.commit()` |
| Read a record | `db.query().filter().first()` or `.all()` |

- **Always commit** after making changes — without `db.commit()`, changes are not saved to the database
- **Always refresh** after add/update to sync the Python object with the latest database state
- **Do not refresh after delete** — the object no longer exists

---

## SQLAlchemy Error: Existing Database Schema Conflict

If changes are made to the database model after the database file has already been created, SQLAlchemy may throw errors due to schema mismatch.

**Fix:** Delete the existing `.db` file and restart the application. SQLAlchemy will recreate the database with the updated schema.

```bash
# Delete the database file (example)
rm users.db
```

Then restart the Uvicorn server — the database is recreated automatically via `Base.metadata.create_all(bind=engine)`.

---

## Endpoint Summary

| Method | Endpoint | Function | Description |
|--------|----------|----------|-------------|
| `GET` | `/` | `root` | Welcome message |
| `POST` | `/users/` | `create_user` | Create a new user |
| `GET` | `/users/{user_id}` | `get_user` | Get a single user by ID |
| `PUT` | `/users/{user_id}` | `update_user` | Update a user by ID |
| `DELETE` | `/users/{user_id}` | `delete_user` | Delete a user by ID |
| `GET` | `/users/` | `get_all_users` | Get all users |

---

## Complete File Structure Reference

```python
# --- Imports ---
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from typing import Optional, List

# --- App Init ---
app = FastAPI(title="Integration with SQL - Code with Josh")

# --- Database Setup ---
engine = create_engine("sqlite:///./users.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- Database Model ---
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String, unique=True, nullable=False)
    role = Column(String, nullable=True)

Base.metadata.create_all(bind=engine)

# --- Pydantic Models ---
class UserCreate(BaseModel):
    name: str
    email: str
    role: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str

    class Config:
        from_attributes = True

# --- Dependency ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Endpoints ---
@app.get("/")
def root():
    return {"message": "Intro to FastAPI with SQL - Subscribe"}

@app.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    new_user = User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User does not exist")
    for field, value in user.dict().items():
        setattr(db_user, field, value)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User does not exist")
    db.delete(db_user)
    db.commit()
    return {"message": "User deleted"}

@app.get("/users/", response_model=List[UserResponse])
def get_all_users(db: Session = Depends(get_db)):
    return db.query(User).all()
```