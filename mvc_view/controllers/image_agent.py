"""Image agent consumer for display/external services.

This worker consumes summarized news from Kafka, calls the image microservice
(`x/image_service.py`) to fetch & upload an image, and produces enriched messages
to `news.final`. Kept under `x/` to avoid changing the MVC app code.
"""
import os
import time
import requests
from mvc_view.models.kafka_utils import get_producer, get_consumer

IMAGE_URL = os.environ.get("IMAGE_SERVICE_URL", "http://127.0.0.1:8004/image_candidates")
HEADERS = {"Authorization": os.environ.get("IMAGE_SERVICE_TOKEN", "Bearer dev-token")}

# Optional comma-separated list of topics the agent should process.
# If empty or not set, agent processes all topics.
_IMAGE_TOPICS = os.environ.get("IMAGE_TOPICS", "")
if _IMAGE_TOPICS:
    ALLOWED_TOPICS = {t.strip().lower() for t in _IMAGE_TOPICS.split(",") if t.strip()}
else:
    ALLOWED_TOPICS = None


def run():
    producer = get_producer()
    consumer = get_consumer("news.summarized", "image-service")

    print("🖼 Image Agent listening to 'news.summarized'...")

    for msg in consumer:
        try:
            news = msg.value
            title = news.get("title") or news.get("subject") or "(no title)"

            # Prefer explicit 'topic' in message, fall back to 'category'
            topic = news.get("topic") or news.get("category") or "news"
            topic_norm = (topic or "").strip().lower()

            # If IMAGE_TOPICS is set, skip messages not in the allowed list
            if ALLOWED_TOPICS is not None and topic_norm not in ALLOWED_TOPICS:
                print(f"🔕 Skipping '{title}' (topic='{topic_norm}' not in IMAGE_TOPICS)")
                continue

            print(f"\n📥 Received: {title} (topic: {topic})")

            # Query uses the topic (or category) to fetch relevant images
            query = topic if topic else "news"
            res = requests.post(
                IMAGE_URL, json={"query": query}, headers=HEADERS, timeout=20
            )
            res.raise_for_status()
            out = res.json()
            news["image_url"] = out.get("cloudinary_url") or out.get("image_url")

            producer.send("news.final", news)
            producer.flush()
            print(f"✅ Sent to 'news.final' → {title}")

        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(3)


if __name__ == "__main__":
    run()
