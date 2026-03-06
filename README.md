# kintsugi-stack-fastapi

# FastAPI Comprehensive Guide: Photo & Video Sharing API
- Source: https://www.youtube.com/watch?v=SR5NYCdzKkc

## Project Overview
This project involves building a production-grade, back-end API for a photo and video sharing application, similar to the early days of Instagram. The application allows users to sign in, view a feed of photos and videos (with dates and posting users), and upload media. The backend handles advanced concepts including authentication, authorization, logging in users, connecting to a database, and handling file uploads.

## Core Concepts of Web Apps and APIs

### What is an API?
**API** stands for **Application Programming Interface**. It is essentially a back-end framework running on a secure server that facilitates the access and control of data (like user accounts, image, or video posts). The **front-end** (or **client**) is the visual interface users interact with (e.g., a website). The front-end communicates with the API to perform secure operations. 

### URLs and Endpoints
A **URL** (Uniform Resource Locator) consists of several core components:
*   **Domain**: The website space (e.g., `techwithtim.net`, ending in `.com`, `.net`, etc.).
*   **Path (or Endpoint)**: The specific route, page, or resource being accessed from the domain (e.g., `/courses/python` or `/api/post`). APIs use custom endpoints to control access to particular resources.
*   **Query Parameter**: Extra information used to filter a page or retrieve specific data. It always comes after a question mark `?` and multiple parameters are separated by ampersands `&` (e.g., `?video=123&page=2`).

![alt text](image.png)

### The Request and Response Structure
The communication flow between a front-end (client) and back-end (API) is handled via **Requests** and **Responses**.

**Request Components (Client to API)**:
*   **Type / Method**: Indicates what the front-end wants to do.
    *   **GET**: Retrieve data.
    *   **POST**: Create new data.
    *   **PUT / PATCH**: Update existing data.
    *   **DELETE**: Delete data.
*   **Path**: The endpoint being accessed.
*   **Body (Optional)**: Additional data sent with the request (e.g., an image being uploaded, a post caption).
*   **Headers**: Additional information, typically related to authentication (e.g., tokens indicating the user is signed in).

**Response Components (API to Client)**:
*   **Status Code**: A number indicating the outcome of the request.
    *   **200**: OK / Successful.
    *   **201**: Created successfully.
    *   **204**: Updated successfully.
    *   **404**: Not found.
    *   **403**: Unauthorized / Permission required.
    *   **500**: Internal server error.
*   **Body**: Additional data returned to the front-end (e.g., the requested post data). Format is often defined by the headers.
*   **Headers**: Security information, authentication details, or data types (e.g., `application/json`).

![alt text](image-1.png)

![alt text](image-2.png) Simple APIs Example

![alt text](image-3.png)

![alt text](image-4.png)

### JWT Authentication Primer
**JWT (JSON Web Tokens)** are used for authenticated APIs to identify users and verify authorizations securely. 
1.  A user logs in by sending their username and password to an authentication endpoint.
2.  The API verifies the credentials and returns a signed **JWT token** (a random string identifying the specific user).
3.  The client stores this token and sends it along in the headers of all future requests.
4.  The API verifies the token on every request to ensure the user has permission to perform the action.

![alt text](image-5.png)

## Environment and Setup

### Project Initialization
It is highly recommended to use **PyCharm** for heavy Python projects due to its support. 
1.  Open a new folder in your editor.
2.  Use a package manager like `uv` (a modern, highly efficient alternative to `pip`) to initialize the project and isolate dependencies.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install uv
```
```bash
uv init .
```
This creates isolated dependencies in your folder, generating a `main.py` and a `pyproject.toml` file.

### Installing Dependencies
Run the following commands to install necessary dependencies:
```bash
uv add fastapi
uv add python-dotenv
uv add fastapi-users[sqlalchemy]
uv add imagekitio
uv add uvicorn[standard]
uv add aiosqlite
uv add streamlit
```

### Environment Variables (.env)
Sensitive credentials, tokens, and keys must be stored in a `.env` file. 

Create an account on **ImageKit** (a free service for hosting, managing, and optimizing images/videos as a Digital Asset Management system). Retrieve the public key, private key (requires account password confirmation), and URL endpoint from the developer options.

Create a `.env` file in the root directory:
```env
IMAGEKIT_PRIVATE_KEY=your_private_key
IMAGEKIT_PUBLIC_KEY=your_public_key
IMAGEKIT_URL_ENDPOINT=your_url_endpoint
```

## Creating the FastAPI Application

### Scaffolding
Create a directory named `app` (or `src/app`) to hold the application code, and inside it, create an `app.py` file. This file initializes the FastAPI instance.

```python
from fastapi import FastAPI

app = FastAPI()
```

### Creating Your First Endpoint
Endpoints are defined using decorators containing the HTTP method (e.g., `@app.get`) and the path. FastAPI functions typically return a Pydantic object or a Python dictionary (which represents **JSON** - JavaScript Object Notation).

```python
@app.get("/hello-world")
def hello_world():
    return {"message": "hello world"}
```

### Running the Server with Uvicorn
Modify the root `main.py` file to run the application using **Uvicorn**, an asynchronous web server.

```python
import uvicorn

if __name__ == "__main__":
    uvicorn.run("app.app:app", host="0.0.0.0", port=8000, reload=True)
```
*   `"app.app:app"`: Targets the `app` variable inside the `app.py` file within the `app` directory.
*   `host="0.0.0.0"`: Runs the server on any available domain (accessible via localhost `127.0.0.1` or the machine's private IP address on the network).
*   `port=8000`: Specifies the port.
*   `reload=True`: Automatically shuts down and restarts the server anytime changes are saved, which is highly useful for debugging.

Run the server via the terminal:
```bash
uv run main.py
```

![alt text](image-6.png)

```
http://localhost:8000/

{"detail":"Not Found"}
```

### Interactive Documentation
FastAPI automatically generates comprehensive documentation allowing you to execute and test endpoints directly from the browser.
*   **Swagger UI**: Navigate to `/docs` to see endpoints, configuration, and a "Try it out" button for sending test requests.
*   **ReDoc**: Navigate to `/redoc` for an alternative, modern documentation view.

![alt text](image-7.png)
![alt text](image-8.png)

## Routing and Parameters

### Path Parameters
Path parameters are dynamic values placed in the URL (enclosed in curly braces `{}`) to filter specific resources. Providing Python type hints (e.g., `id: int`) enables FastAPIs automatic data validation; it will reject invalid data types.

```python
from fastapi import HTTPException

text_posts = {1: {"title": "new post", "content": "cool test post"}}

@app.get("/posts/{id}")
def get_post(id: int):
    if id not in text_posts:
        raise HTTPException(status_code=404, detail="post not found")
    return text_posts.get(id)
```

### Query Parameters
Query parameters are optional or mandatory variables passed directly into the endpoint function. Assigning a default value (like `None`) makes them optional.

```python
@app.get("/posts")
def get_all_posts(limit: int | None = None):
    if limit:
        return list(text_posts.values())[:limit]
    return list(text_posts.values())
```

## Pydantic Schemas and Data Validation

### Request Bodies
For `POST`, `PUT`, or `PATCH` requests, data is typically sent in the **request body**. FastAPI uses Pydantic **schemas** to define and validate this data structure. Create a `schemas.py` file for these definitions.

```python
# schemas.py
from pydantic import BaseModel

class PostCreate(BaseModel):
    title: str
    content: str
```

When importing and using this schema in an endpoint, FastAPI strictly validates that incoming request bodies match the schema types before executing the function.

```python
# app.py
from app.schemas import PostCreate

@app.post("/post")
def create_post(post: PostCreate):
    new_id = max(text_posts.keys()) + 1
    new_post = {"title": post.title, "content": post.content}
    text_posts[new_id] = new_post
    return new_post
```

### Response Models
Specifying a response type using an arrow `->` or the `response_model` parameter improves API documentation (showing exact return formats in `/docs`) and adds a layer of protection. If the function attempts to return data missing fields defined in the response schema, FastAPI automatically raises an error.

## Database Setup (SQLAlchemy)

To store data persistently (preventing data loss on server refresh), an **ORM (Object Relational Mapping)** is used. SQLAlchemy allows writing Python-like code to define, retrieve, create, and update data instead of writing manual SQL queries.

### Creating Data Models
Create a `db.py` file to handle database architecture. The `Base` class must inherit from `DeclarativeBase` to mark classes as data models.

```python
# db.py
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, relationship

class Base(DeclarativeBase):
    pass

class Post(Base):
    __tablename__ = "post"
    
    # Primary Key must be unique. Automatically generates a unique UUID4.
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    caption = Column(Text)
    url = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    file_name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
```
*Note: A primary key represents the unique lookup entity for an entry in the database.*

### Async Engine and Session Initialization
Configure the connection to an asynchronous SQLite database locally for testing. 

```python
# db.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from collections.abc import AsyncGenerator

DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

# Creates tables in the database automatically finding classes inheriting from Base
async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Asynchronous generator to yield a database session
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
```

### Lifespan Context Manager
In `app.py`, link the table creation to the FastAPI startup process using a lifespan asynchronous context manager. This guarantees the database is ready when the server boots.

```python
# app.py
from contextlib import asynccontextmanager
from app.db import create_db_and_tables

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)
```

## Handling Image and Video Uploads

### Integrating ImageKit
Create an `images.py` file to handle environment variables and ImageKit initialization. Variables are loaded exclusively on the back-end to prevent front-end security token exposure.

```python
# images.py
import os
from dotenv import load_dotenv
from imagekitio import ImageKit

load_dotenv()

imagekit = ImageKit(
    private_key=os.getenv("IMAGEKIT_PRIVATE_KEY"),
    public_key=os.getenv("IMAGEKIT_PUBLIC_KEY"),
    url_endpoint=os.getenv("IMAGEKIT_URL_ENDPOINT")
)
```

### File Upload Endpoint
Uploads require `multipart/form-data` instead of standard JSON request bodies. FastAPIs `UploadFile` receives the file object.

Because server-side uploading (Backend Upload) is more secure, the API receives the file, duplicates it to a temporary file, uploads it to ImageKit, and then deletes the local temporary file.

```python
# app.py
import tempfile
import shutil
import os
from fastapi import File, UploadFile, Form, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from imagekitio.models.UploadFileRequestOptions import UploadFileRequestOptions

from app.db import Post, get_async_session
from app.images import imagekit

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...), 
    caption: str = Form(...), 
    session: AsyncSession = Depends(get_async_session)
):
    temp_file_path = None
    try:
        # Create temporary file matching the extension of the uploaded file
        _, ext = os.path.splitext(file.filename)
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp_file:
            temp_file_path = temp_file.name
            shutil.copyfileobj(file.file, temp_file)
            
        # Upload the temporary file to ImageKit
        with open(temp_file_path, "rb") as f:
            options = UploadFileRequestOptions(use_unique_file_name=True, tags=["backend_upload"])
            upload_result = imagekit.upload_file(
                file=f,
                file_name=file.filename,
                options=options
            )
            
        if upload_result.response_metadata.http_status_code == 200:
            file_type = "video" if file.content_type.startswith("video/") else "image"
            
            # Database storage operations
            post = Post(
                caption=caption,
                url=upload_result.url,
                file_type=file_type,
                file_name=upload_result.name
            )
            session.add(post)
            await session.commit()
            await session.refresh(post) # Hydrates object with auto-generated ID & created_at
            
            return post
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Clean up file structures to avoid memory leaks
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        file.file.close()
```
*Note: `Depends(get_async_session)` is an example of Dependency Injection. It runs the provided function and passes the return value dynamically as a variable into the endpoint.*

## CRUD Operations (Create, Read, Delete)

### Retrieving Data (Read)
Use SQLAlchemy's `select` to query the database. To extract results dynamically, loop over the rows or use `.scalars().all()`.

```python
from sqlalchemy import select

@app.get("/feed")
async def get_feed(session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(Post).order_by(Post.created_at.desc()))
    posts = [row for row in result.all()]
    
    post_data = []
    for post in posts:
        post_data.append({
            "id": str(post.id),
            "caption": post.caption,
            "url": post.url,
            "file_type": post.file_type,
            "file_name": post.file_name,
            "created_at": post.created_at.isoformat()
        })
    return post_data
```

### Deleting Data
Requires verifying exact matches (converting strings to UUIDs where necessary).

```python
import uuid

@app.delete("/post/{post_id}")
async def delete_post(post_id: str, session: AsyncSession = Depends(get_async_session)):
    try:
        post_uuid = uuid.UUID(post_id)
        result = await session.execute(select(Post).where(Post.id == post_uuid))
        post = result.scalars().first()
        
        if not post:
            raise HTTPException(status_code=404, detail="post not found")
            
        await session.delete(post)
        await session.commit()
        
        return {"success": True, "message": "post deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## User Authentication (FastAPI Users)

To secure the application with JWT, the `fastapi-users` library automates standard processes (registration, login, verifying tokens).

### Database Relationships
A **one-to-many** relationship links one user to many posts. The "child" (Post) holds the `ForeignKey` linking it to the parent (User).

```python
# db.py
from fastapi_users.db import SQLAlchemyBaseUserTableUUID, SQLAlchemyUserDatabase

class User(SQLAlchemyBaseUserTableUUID, Base):
    posts = relationship("Post", back_populates="user")

# Update the Post class
class Post(Base):
    # ... existing fields ...
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    user = relationship("User", back_populates="posts")

async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)
```

### JWT Strategy and User Manager
Create a `users.py` file to handle authentication backend configuration. Note that `SECRET` should be a complex, unshared string used to encode tokens.

```python
# users.py
import uuid
from typing import Optional
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin
from fastapi_users.authentication import AuthenticationBackend, BearerTransport, JWTStrategy
from app.db import User, get_user_db

SECRET = "super_secret_string"

class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET
    
    # Custom hooks are supported (e.g., on_after_register)

async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)

bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")

def get_jwt_strategy() -> JWTStrategy:
    # Set lifespan to 3600 seconds (1 hour)
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy
)

fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend]
)

current_active_user = fastapi_users.current_user(active=True)
```
*Note: Token lifetime dictates how long a token is valid before requiring a re-login. Longer limits are convenient but pose security vulnerabilities.*

### Injecting Auth Routes
In `app.py`, inject the pre-built routing functionalities mapped to custom `UserRead`, `UserCreate`, and `UserUpdate` Pydantic schemas (inheriting from `schemas.BaseUser` in `schemas.py`).

```python
# app.py
from app.users import auth_backend, current_active_user, fastapi_users
from app.schemas import UserRead, UserCreate, UserUpdate

app.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"]
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate), prefix="/auth", tags=["auth"]
)
# Other routers like password reset and user routing can be appended similarly
```

### Protecting Endpoints
To make a route protected (requiring a user to be signed in), pass the `current_active_user` as a dependency.

```python
@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...), 
    caption: str = Form(...), 
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user) # Protects route and binds active user
):
    # Store user identity on the post payload
    post = Post(..., user_id=user.id)
```

Additionally, apply authorization logic within the function (e.g., verifying `post.user_id == user.id` before allowing deletions) to enforce user-specific permissions.

## ImageKit API URL Transformations
ImageKit allows real-time dynamic manipulation of files directly through query strings or URL paths, enhancing UI flexibility without reprocessing base files.
*   **Cropping/Sizing**: `tr=w-300,h-300` directly modifies width and height.
*   **Enhancements**: `tr=e-contrast` (increases contrast), `tr=e-sharpen` (sharpens image).
*   **Text/Overlays**: Add captions via URL string overlays, modifying sizes using attributes like `font-size_100`.
*   **Videos**: Output frames as thumbnails via appending `ik-thumbnail.jpg` (or requesting specific timeframes like 5 seconds in). Videos can also be cropped into vertical frames with blurred backgrounds, and drastically optimized (e.g., 90% quality compression makes files 3x smaller without major quality loss).

## Front-End Integration (Streamlit context)
A simple frontend like Streamlit interfaces with the backend by executing HTTP operations mapped to the API. Once the backend successfully registers or logs in the user (`/auth/jwt/login`), the frontend saves the resulting access token into a session state. For any protected operations (like viewing the feed or uploading files), this token is included in the request headers (formatted as `Bearer <token>`).