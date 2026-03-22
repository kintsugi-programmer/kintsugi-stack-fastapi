# images.py
from dotenv import load_dotenv
from imagekitio import ImageKit
import os

load_dotenv()

imagekit = ImageKit(
    private_key=os.getenv("IMAGEKIT_PRIVATE_KEY"),
    # public_key=os.getenv("IMAGEKIT_PUBLIC_KEY"), # old
    # url_endpoint=os.getenv("IMAGEKIT_URL_ENDPOINT") # old
)

# Store URL endpoint for reuse
URL_ENDPOINT = os.environ.get("IMAGEKIT_URL_ENDPOINT")

# uv pip install imagekitio==5.2.0
# imagekit is a client library for ImageKit, which is a cloud-based image and video management service. It provides a simple and easy-to-use interface for uploading, transforming, and delivering images and videos.