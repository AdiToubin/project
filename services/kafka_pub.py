from kafka import KafkaProducer

class Producer:
    ##חיבור לקפקא

    def __init__(self, configs):
        self.configs = configs
        self.producer = None

###פתיחת החיבור
    def open(self):
        try:
            self.producer = KafkaProducer(**self.configs)
        except Exception as e:
            raise RuntimeError("Failed to connect to Kapka.") from e

###סגירת החיבור
    def close(self):
        if self.producer:
            self.producer.close()

###שליחת הודעה לקפקא
    def send_to_kafka(self, topic_name, data):
        try:
            self.producer.send(topic_name, data)

        except Exception as e:
            raise RuntimeError("Failed to send to Kapka") from e
## השירות של קפקא היצרן איתו מעבירים לטבלת נתונים לפי הפונקציות