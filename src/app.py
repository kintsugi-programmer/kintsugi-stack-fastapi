# app.py
from fastapi import FastAPI, HTTPException
from src.schemas import PostCreate, PostResponse

application = FastAPI()

@application.get("/hello-world")
def hello_world():
    return {"message":"hello world !!!"}

# text_posts = {
#     1 : {"title":"new post", "content": "cool test post"}
# }

text_posts = {
    1: {"title": "Morning Coffee", "content": "Started the day with a strong cup of coffee."},
    2: {"title": "Learning FastAPI", "content": "Building my first API with FastAPI today."},
    3: {"title": "Debugging Code", "content": "Spent an hour fixing a small bug."},
    4: {"title": "New Project Idea", "content": "Thinking about building a health tech platform."},
    5: {"title": "Database Setup", "content": "Installed PostgreSQL and created a new database."},
    6: {"title": "API Testing", "content": "Testing endpoints using Postman."},
    7: {"title": "Late Night Coding", "content": "Still coding at midnight."},
    8: {"title": "Learning Git", "content": "Practicing commits and branches today."},
    9: {"title": "Reading Docs", "content": "Reading FastAPI documentation."},
    10: {"title": "Weekend Build", "content": "Working on a small backend project."}
}

# @application.get("/posts")
# def get_all_posts():
#     return text_posts

@application.get("/post/{id}")
def get_post(id:int):
    if id not in text_posts:
        raise HTTPException(status_code=404, detail="post not found")
    return text_posts.get(id)

@application.get("/posts")
def get_all_posts(limit: int = None)  -> PostResponse: # here parameter is written because FastAPI will Auto Document it and Validate it
    if limit:
            return list(text_posts.values())[:limit]
    return text_posts

@application.post("/post")
def create_post(post_body: PostCreate) -> PostResponse : # validates incoming (PostCreate) and Outgoing (PostResponse), if not valid so raise error
    new_id = max(text_posts.keys()) + 1
    new_post = { "title": post_body.title , "content" : post_body.content }
    text_posts[new_id] = new_post
    return new_post