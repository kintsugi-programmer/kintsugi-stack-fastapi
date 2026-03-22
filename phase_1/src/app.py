# app.py
from fastapi import FastAPI, HTTPException, File, UploadFile, Depends, Form
from src.schemas import PostCreate, PostResponse, UserRead, UserCreate, UserUpdate # new
from src.db import Post, create_db_and_tables, get_async_session, User # new
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from contextlib import asynccontextmanager
from src.images import imagekit
# from imagekitio.models.UploadFileRequestOptions import UploadFileRequestOptions
import shutil
import os
import uuid
import tempfile
from src.users import fastapi_users, current_active_user, auth_backend # new


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables() # create db for us, and make sure  this is essentially handled correctly and cleanly . at time of exit, it will close the connection to the database, so that we don't have any connection leaks, and we can ensure that our application is properly cleaned up when it shuts down.
    yield

application = FastAPI(lifespan=lifespan)

application.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"]
) # in my app i want to include the authentication routes provided by fastapi_users, so that i can use JWT authentication in my app, and i want to prefix all the auth routes with /auth/jwt, so that i can easily identify them in my API documentation, and also group them together in the documentation under the "auth" tag.
application.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"]
) # this will create the registration route for us, and we can use it to register new users, and we can also specify the UserRead and UserCreate schemas that we want to use for the registration route, so that we can validate the incoming data for the registration route, and also specify the response model for the registration route, so that we can validate the outgoing data for the registration route.
application.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"]
) # this will create the reset password route for us, and we can use it to reset the password for existing users.
application.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"]
) # this will create the verify route for us, and we can use it to verify for existing users.
application.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"]
) # this will create the user management routes for us, such as /users/me, /users/{id}, etc. and we can use these routes to manage the users in our application, such as getting the current user, updating the user information, etc. and we can also specify the UserRead and UserUpdate schemas that we want to use for these routes, so that we can validate the incoming data for these routes, and also specify the response model for these routes, so that we can validate the outgoing data for these routes.


@application.post("/upload") # using async, fastapi is async framework
async def upload_file(
    file: UploadFile = File(...),
    user: User = Depends(current_active_user), # this will ensure that only authenticated users can access this route, and it will also give us the current user object that we can use in our route, so that we can associate the uploaded file with the user who uploaded it, and we can also use the user information for any other purpose that we want in this route, such as logging, etc.
    caption: str = Form(""),
    session: AsyncSession = Depends(get_async_session) # FastAPI Dependency Injection, it will automatically create a new session for each request and close it after the request is done
) : 

    temp_file_path = None
    try: 
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            temp_file_path = temp_file.name
            shutil.copyfileobj(file.file, temp_file)
        
        upload_result = imagekit.files.upload(
        # upload_result = imagekit.upload_file( # old

            file=open(temp_file_path, "rb"),
            file_name=file.filename,
            folder="/products",
            tags=["product", "featured"]
            # options=UploadFileRequestOptions( # old
            #     use_unique_file_name=True,
            #     tags=["backend-upload"]
            # )
        )
        if upload_result and upload_result.url :
        # if upload_result.status_code == 200: # old
            post = Post( 
                # endpoint protect
                user_id = user.id, # storing user for every single post
                # dummy post 
                caption = caption,
                # url = "dummy url",
                url = upload_result.url,
                # file_type = "photo",
                file_type = "video" if file.content_type.startswith("video/") else "photo",
                # file_name = "dummy name"
                file_name = upload_result.name
            )
            session.add(post)
            await session.commit()
            await session.refresh(post)
            return post
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        # pass
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        file.file.close()


    # dummy
    # post = Post( # dummy post 
    #     caption = caption,
    #     url = "dummy url",
    #     file_type = "photo",
    #     file_name = "dummy name"
    # )
    # session.add(post) # like staging, post is added to session but not saved
    # await session.commit() # like commit, saving the post to the database
    # # id and created_at are generated by the database, so we need to refresh the post object to get the updated data from the database, because after commit, the post object is not updated with the data from the database, so we need to refresh it to get the id of the post
    # # after commit, the post object is not updated with the data from the database, so we need to refresh it to get the id of the post
    # await session.refresh(post) # like refresh, refreshing the post object with the data from the database, so that we can get the id of the post
    # return post

@application.get("/feed")
async def get_feed(
    session: AsyncSession = Depends(get_async_session)
    ,user: User = Depends(current_active_user) # protect endpoint
):
    result = await session.execute(select(Post).order_by(Post.created_at.desc())) # like select * from posts order by created_at desc, it will return a list of Post objects
    posts = [row[0] for row in result.all()] # result.all() will return a list of tuples, where each tuple contains a single Post object, so we need to extract the Post object from the tuple using row[0]
    # cursor object is returned by the database, and we need to convert it to a list of Post objects, so that we can return it as a response

    result = await session.execute(select(User))
    users = [ row[0] for row in result.all()]
    users_dict = {u.id: u.email for u in users}

    posts_data = []
    for post in posts:
        posts_data.append({
            "id":str(post.id),
            "user_id":str(post.user_id),
            "caption":post.caption,
            "url":post.url,
            "file_type":post.file_type,
            "file_name":post.file_name,
            "created_at":post.created_at.isoformat(),
            "is_owner": post.user_id == user.id # this will add a field to the response that indicates whether the current user is the owner of the post or not, so that the client can use this information to determine whether to show edit/delete options for the post or not, because only the owner of the post should be able to edit or delete the post, so we need to provide this information in the response, so that the client can make the appropriate UI decisions based on this information.
            ,"email": users_dict.get(post.user_id, "Unknown") 
        })
    
    return {"posts": posts_data}

@application.delete("/post/{post_id}")
async def delete_post(
    post_id: str,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user) # protect endpoint
    ):
    try: 
        post_uuid = uuid.UUID(post_id) # convert the post_id string to a UUID object, if the post_id is not a valid UUID, it will raise a ValueError, so we need to handle that exception and return a 400 Bad Request error to the client, because the client has sent an invalid post_id, so we need to inform them about the error in their request
        result = await session.execute(select(Post).where(Post.id == post_uuid))  # like select * from posts where id = post_id, it will return a list of Post objects that match the condition, but since id is unique, it will return either one Post object or None
        post = result.scalars().first() # scalars() will return a list of Post objects, and first() will return the first Post object from the list, or None if the list is empty

        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

        # endpoint protect
        if post.user_id != user.id: # check if the user who is trying to delete the post is the owner of the post, if not, then we need to return a 403 Forbidden error, because the user is not authorized to delete this post
            raise HTTPException(status_code=403, detail="You are not authorized to delete this post")
        
        await session.delete(post) # like delete from posts where id = post_id, it will delete the post from the database, but we need to commit the transaction to make sure that the changes are saved to the database, so we need to call session.commit() after deleting the post
        await session.commit()
        return {"success":True, "message":"Post deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# old stuff rewamp

# @application.get("/hello-world")
# def hello_world():
#     return {"message":"hello world !!!"}

# # text_posts = {
# #     1 : {"title":"new post", "content": "cool test post"}
# # }

# text_posts = {
#     1: {"title": "Morning Coffee", "content": "Started the day with a strong cup of coffee."},
#     2: {"title": "Learning FastAPI", "content": "Building my first API with FastAPI today."},
#     3: {"title": "Debugging Code", "content": "Spent an hour fixing a small bug."},
#     4: {"title": "New Project Idea", "content": "Thinking about building a health tech platform."},
#     5: {"title": "Database Setup", "content": "Installed PostgreSQL and created a new database."},
#     6: {"title": "API Testing", "content": "Testing endpoints using Postman."},
#     7: {"title": "Late Night Coding", "content": "Still coding at midnight."},
#     8: {"title": "Learning Git", "content": "Practicing commits and branches today."},
#     9: {"title": "Reading Docs", "content": "Reading FastAPI documentation."},
#     10: {"title": "Weekend Build", "content": "Working on a small backend project."}
# }

# # @application.get("/posts")
# # def get_all_posts():
# #     return text_posts

# @application.get("/post/{id}") 
# def get_post(id:int)-> PostResponse:
#     if id not in text_posts:
#         raise HTTPException(status_code=404, detail="post not found")
#     return text_posts.get(id)

# @application.get("/posts")
# def get_all_posts(limit: int = None)  : # here parameter is written because FastAPI will Auto Document it and Validate it
#     if limit:
#             return list(text_posts.values())[:limit]
#     return text_posts

# @application.post("/post")
# def create_post(post_body: PostCreate) -> PostResponse : # validates incoming (PostCreate) and Outgoing (PostResponse), if not valid so raise error
#     new_id = max(text_posts.keys()) + 1
#     new_post = { "title": post_body.title , "content" : post_body.content }
#     text_posts[new_id] = new_post
#     return new_post