#התקשורת בין המערכת שלנו לקפקא#
import json
from typing import Any
from kafka import KafkaProducer, KafkaConsumer

#* הפונקציה יוצרת רכיב ששולח הודעות לקפקא*#
#*שייכת לשכבה הזו כי היא אחראית על תקשורת חיצונית, שליחה לקפקא, היא הרי לא מציגה כלום למשתמש וגם לא שומרת נתונים קבועים*#
def get_producer(bootstrap_servers: str = "localhost:9092") -> KafkaProducer:
    return KafkaProducer(
        bootstrap_servers=bootstrap_servers,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )

#* הפונקציה יוצרת רכיב שקורא הודעות למערכת קפקא*#
# שייכת לשכבה הזו כי היא מקבלת נתונים מהקפקא, מקור חיצוני, ומעבירה אותם למערכת שלנו#
def get_consumer(topic: str, group_id: str, bootstrap_servers: str = "localhost:9092") -> KafkaConsumer:
    return KafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        group_id=group_id,
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    )
