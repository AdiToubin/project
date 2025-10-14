import json
from ingest_articles import ingest_payload

with open("news.json", "r", encoding="utf-8") as f:
    payload = json.load(f)

result = ingest_payload(payload, table_name="articles")
print(result)
