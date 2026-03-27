# FastAPI Fundamentals: CRUD API with Pydantic, Uvicorn & Swagger UI

- res: https://youtu.be/nWWPlEO0he8?si=3ammbUmb4EMSCqN3

---

## Overview

This minicourse covers everything needed to get started with FastAPI, including:

- Setting up FastAPI
- Understanding and building API endpoints
- Creating Pydantic models
- Performing all CRUD operations (GET, POST, PUT, DELETE)
- Using the built-in Swagger UI to test the API
- Searching through data

---

## What is FastAPI?

- **FastAPI** is a Python framework for building APIs
- Alternatives include **Flask** and **Django**, but FastAPI is lighter and more focused on the API side of things
- FastAPI is *lighter than Flask*, so it is run differently (using Uvicorn, not directly with Python)

---

## CRUD Operations and HTTP Requests

**CRUD** stands for:

| CRUD Operation | HTTP Request | Description |
|---|---|---|
| **Create** | `POST` | Send/post information to the API |
| **Read** | `GET` | Retrieve/read information from the API |
| **Update** | `PUT` | Put new/updated information into the data store |
| **Delete** | `DELETE` | Remove information from the data store |

---

## Installation

Install the following packages:

```bash
pip install fastapi
pip install pydantic
pip install uvicorn
```

> If `pip install uvicorn` fails, try running it as a module:
> ```bash
> python -m pip install uvicorn
> ```

---

## Running the API

FastAPI cannot be run directly with `python myfile.py`. It requires **Uvicorn**:

```bash
uvicorn my_api:app --reload
```

- `my_api` — the name of the Python file (without `.py`)
- `app` — the name of the FastAPI instance created in the file
- `--reload` — automatically reloads on code changes (similar to `debug=True` in Flask)

Once running, the API is accessible at:

```
http://127.0.0.1:8000
```

---

## Swagger UI (Docs)

FastAPI automatically generates interactive API documentation. Access it at:

```
http://127.0.0.1:8000/docs
```

- Built on **Swagger UI**
- Displays all created endpoints
- Allows testing each endpoint directly in the browser without any external tool

---

## Project Setup

### Imports

```python
from fastapi import FastAPI, HTTPException, status, Path
from typing import Optional
from pydantic import BaseModel
```

**Import breakdown:**

- `FastAPI` — the main class used to create the API instance
- `HTTPException` — used to raise HTTP errors with status codes and detail messages
- `status` — provides named HTTP status code constants (e.g., `status.HTTP_201_CREATED`)
- `Path` — used to add validation constraints to path parameters (e.g., must be greater than 0)
- `Optional` — from `typing`; marks Pydantic model fields as not required
- `BaseModel` — from `pydantic`; base class for creating data models

### Creating the FastAPI Instance

```python
app = FastAPI()
```

- `app` is an instance of the `FastAPI` class
- This object builds out the entire API
- All route decorators are called on this object (e.g., `@app.get(...)`)

---

## Endpoints

An **endpoint** is a URL path that the API exposes. Examples:

- `/` — the root/landing page
- `/users/{user_id}` — a specific user
- `/users/search` — search for a user

Every endpoint beyond the root is an extension of the base URL.

---

## Mock Data (In Place of a Database)

In this minicourse, a Python dictionary is used instead of a real database (e.g., PostgreSQL, MongoDB):

```python
users = {
    1: {
        "name": "Josh",
        "website": "zero2knowing.com",
        "age": 28,
        "role": "developer"
    }
}
```

- Keys are integer user IDs (starting at 1, incrementing)
- Values are dictionaries containing user details
- In a real-world application, this would be replaced with a database

> **Note:** Because a plain dictionary is used, all data resets every time the server reloads or the page is refreshed.

---

## Pydantic Models

Pydantic models enforce **data types** on incoming data. If a wrong data type is provided, FastAPI automatically returns an error.

### User Model (for creating a user)

```python
from pydantic import BaseModel

class User(BaseModel):
    name: str
    website: str
    age: int
    role: str
```

- Inherits from `BaseModel`
- All fields are **required**
- Behaves similarly to a Python dataclass
- Automatically validates data types on input

### UpdateUser Model (for partially updating a user)

```python
from typing import Optional

class UpdateUser(BaseModel):
    name: Optional[str] = None
    website: Optional[str] = None
    age: Optional[int] = None
    role: Optional[str] = None
```

- All fields are **optional**
- If a field is not provided, its value defaults to `None`
- This allows updating only specific fields without requiring all of them
- Used specifically in the PUT (update) endpoint

---

## Endpoints — Full Implementation

### 1. Root Endpoint (Landing Page)

```python
@app.get("/")
def root():
    return {"message": "Welcome to your introduction to FastAPI"}
```

- Uses `@app.get("/")`
- Returns a Python dictionary (equivalent to JSON)
- This is the base/landing page of the API

---

### 2. GET — Retrieve a User

```python
@app.get("/users/{user_id}")
def get_user(user_id: int = Path(description="The ID of the user you want to get", gt=0, lt=100)):
    if user_id not in users:
        raise HTTPException(status_code=404, detail="User not found")
    return users[user_id]
```

**Key details:**

- `{user_id}` is a **path parameter** — it appears in the URL (e.g., `/users/1`)
- `Path(...)` adds validation and documentation to the parameter:
  - `description` — describes what the parameter is for (visible in Swagger UI)
  - `gt=0` — value must be **greater than 0**
  - `lt=100` — value must be **less than 100**
- If the `user_id` is not found in the dictionary, raise a `404 HTTPException` with `"User not found"`
- Otherwise, return the user's data from the dictionary

---

### 3. POST — Create a User

```python
@app.post("/users/{user_id}", status_code=status.HTTP_201_CREATED)
def create_user(user_id: int, user: User):
    if user_id in users:
        raise HTTPException(status_code=400, detail="User already exists")
    users[user_id] = user.dict()
    return user
```

**Key details:**

- Uses `@app.post(...)` because data is being **sent** to the API
- `status_code=status.HTTP_201_CREATED` — returns HTTP 201 on success (meaning "resource was created")
- Accepts a `user_id` path parameter and a `user` object of type `User` (the Pydantic model)
- If the `user_id` already exists, raise a `400 HTTPException` with `"User already exists"`
- `user.dict()` converts the Pydantic model object into a plain Python dictionary for storage
- Returns the created user

---

### 4. PUT — Update a User

```python
@app.put("/users/{user_id}")
def update_user(user_id: int, user: UpdateUser):
    if user_id not in users:
        raise HTTPException(status_code=404, detail="User not found")

    current_user = users[user_id]

    if user.name is not None:
        current_user["name"] = user.name
    if user.website is not None:
        current_user["website"] = user.website
    if user.age is not None:
        current_user["age"] = user.age
    if user.role is not None:
        current_user["role"] = user.role

    return current_user
```

**Key details:**

- Uses `@app.put(...)` because data is being **updated**
- Accepts the `UpdateUser` Pydantic model (all fields optional)
- If the `user_id` does not exist, raise a `404 HTTPException` with `"User not found"`
- Each field is checked individually — only fields that are **not `None`** are updated
- This allows partial updates (e.g., updating only the name without touching other fields)
- Returns the updated user dictionary

---

### 5. DELETE — Delete a User

```python
@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    if user_id not in users:
        raise HTTPException(status_code=404, detail="User not found")

    deleted_user = users.pop(user_id)
    return {"message": "User has been deleted", "deleted_user": deleted_user}
```

**Key details:**

- Uses `@app.delete(...)` to handle delete requests
- If the `user_id` is not found, raise a `404 HTTPException`
- `users.pop(user_id)` removes the user from the dictionary and returns the removed value
- Returns a confirmation message along with the data of the deleted user

---

### 6. GET — Search for a User by Name

```python
@app.get("/users/search")
def search_user(name: Optional[str] = None):
    if not name:
        return {"message": "Name parameter is required"}

    for user in users.values():
        if user["name"] == name:
            return user

    raise HTTPException(status_code=404, detail="User not found")
```

**Key details:**

- Uses `@app.get("/users/search")`
- `name` is a **query parameter** — it is passed in the URL after a `?` (e.g., `/users/search?name=Josh`)
- Query parameters are not part of the path; anything after `?` in a URL is a query
- If `name` is not provided, returns a message saying the parameter is required
- Loops through `users.values()` to search all user records
  - `.values()` returns the inner dictionaries (user data), not the keys (IDs)
- If a match is found, return that user
- If the loop completes without a match, raise a `404 HTTPException` with `"User not found"`

> **Important:** Matching is **case-sensitive**. Searching for `"josh"` will not match `"Josh"`. No case-insensitive handling was implemented in this minicourse.

---

## Error Handling with HTTPException

`HTTPException` is used throughout to return proper HTTP error responses:

```python
raise HTTPException(status_code=404, detail="User not found")
```

- `status_code` — the HTTP status code (e.g., `400`, `404`)
- `detail` — a message explaining the error

**Common status codes used:**

| Code | Meaning |
|---|---|
| `200` | OK (default success) |
| `201` | Created (used when a resource is successfully created) |
| `400` | Bad Request (e.g., user already exists) |
| `404` | Not Found (e.g., user ID not in data) |

---

## Complete File Structure Summary

```
api_course/
└── my_api.py
```

All code lives in a single Python file. No database is used — a Python dictionary acts as the data store.

---

## Key Concepts Recap

- **FastAPI instance (`app`)** — the central object that the entire API is built on
- **Endpoints** — URL paths that define what the API can do
- **Path parameters** — variables embedded in the URL path (e.g., `{user_id}`)
- **Query parameters** — variables passed after `?` in the URL (e.g., `?name=Josh`)
- **Pydantic models** — enforce data type validation on incoming data
- **`BaseModel`** — all required fields; used for creating new resources
- **`Optional` fields** — allow partial data; used for updating existing resources
- **`Path()`** — adds constraints and documentation to path parameters
- **`HTTPException`** — raises HTTP errors with a status code and detail message
- **`status`** — provides readable constants for HTTP status codes
- **`user.dict()`** — converts a Pydantic model to a Python dictionary

---

## Possible Extensions (Mentioned but Not Implemented)

- Adding more fields to the `User` model
- Creating relationships between users
- Connecting to a real database (e.g., PostgreSQL, MongoDB)
- Implementing security features (e.g., authentication, authorization)
- Case-insensitive name search