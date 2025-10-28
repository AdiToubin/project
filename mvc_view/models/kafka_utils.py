import json
from typing import Any
from kafka import KafkaProducer, KafkaConsumer


def get_producer(bootstrap_servers: str = "localhost:9092") -> KafkaProducer:
    return KafkaProducer(
        bootstrap_servers=bootstrap_servers,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )


def get_consumer(topic: str, group_id: str, bootstrap_servers: str = "localhost:9092") -> KafkaConsumer:
    return KafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        group_id=group_id,
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    )
