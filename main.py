# main.py
import uvicorn

def main():
    print("Hello from kintsugi-stack-fastapi!")
    uvicorn.run("src.app:application",host="0.0.0.0",port=8000,reload=True)

if __name__ == "__main__":
    main()
