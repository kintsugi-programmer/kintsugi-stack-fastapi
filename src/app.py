from fastapi import FastAPI 

application = FastAPI()

@application.get("/hello-world")
def hello_world():
    return {"message":"hello world !!!"}
    

