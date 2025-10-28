import os
import time
import json
from dotenv import load_dotenv
from kafka import KafkaConsumer
import requests

load_dotenv()

SUPABASE_URL = (os.getenv("SUPABASE_URL") or "").rstrip("/")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY") or ""
REST_URL = f"{SUPABASE_URL}/rest/v1"
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal",
}


def update_article_image(guid: str | None, subject: str | None, image_url: str) -> bool:
    """Try to update the article row with the image_url.

    Prefer updating by guid, fall back to subject if guid missing.
    Returns True on success.
    """
    if not image_url:
        return False

    if guid:
        url = f"{REST_URL}/articles?guid=eq.{guid}"
        try:
            r = requests.patch(url, headers=HEADERS, json={"image_url": image_url}, timeout=20, verify=False)
            r.raise_for_status()
            return True
        except Exception as e:
            print(f"Failed to update by guid {guid}: {e}")

    if subject:
        # simple equality match; encode subject for URL
        try:
            url = f"{REST_URL}/articles?subject=eq.{requests.utils.quote(subject, safe='')}"
            r = requests.patch(url, headers=HEADERS, json={"image_url": image_url}, timeout=20, verify=False)
            r.raise_for_status()
            return True
        except Exception as e:
            print(f"Failed to update by subject '{subject}': {e}")

    return False


def run():
    consumer = KafkaConsumer(
        "news.final",
        bootstrap_servers="localhost:9092",
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        group_id="image-final-consumer",
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    )

    print("🛠 image_final_consumer listening to 'news.final'...")

    for msg in consumer:
        try:
            news = msg.value
            print("Received final news:", news.get("title") or news.get("subject") or news.get("id"))
            image_url = news.get("image_url") or news.get("cloudinary_url")
            guid = news.get("guid") or news.get("id") or news.get("article_id")
            subject = news.get("title") or news.get("subject")

            ok = update_article_image(guid, subject, image_url)
            if ok:
                print("Updated DB with image for:", subject)
            else:
                print("Could not update DB for:", subject)

        except Exception as e:
            print(f"Error processing message: {e}")
            time.sleep(2)


if __name__ == "__main__":
    run()
