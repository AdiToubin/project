from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
import cloudinary
import cloudinary.uploader
import requests
import uvicorn
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Image Agent")

# הגדרות Cloudinary
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True,
)


class ImageQuery(BaseModel):
    query: str


PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")


@app.post("/image_candidates")
def upload_image(inp: ImageQuery, authorization: str | None = Header(default=None)):
    if authorization != "Bearer dev-token":
        raise HTTPException(status_code=401, detail="Invalid or missing token")

    query = inp.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    # שלב 1: מבצע חיפוש ב־Pexels (או Unsplash)
    headers = {"Authorization": PEXELS_API_KEY}
    res = requests.get(
        f"https://api.pexels.com/v1/search?query={query}&per_page=1", headers=headers
    )
    data = res.json()

    if "photos" not in data or not data["photos"]:
        raise HTTPException(
            status_code=404, detail=f"No image found for query '{query}'"
        )

    # שלב 2: לוקח את ה־URL של התמונה הראשונה
    image_url = data["photos"][0]["src"]["large"]

    # שלב 3: מעלה אותה ל־Cloudinary
    upload_res = cloudinary.uploader.upload(image_url, folder="cloud_news")
    return {
        "query": query,
        "found_image": image_url,
        "cloudinary_url": upload_res["secure_url"],
    }


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8004)
