from confluent_kafka import Consumer, KafkaException
import json
from loguru import logger

class KafkaConsumerService:
    def __init__(self, config, handler):
        self.consumer = Consumer({
            "bootstrap.servers": config["bootstrap_servers"],
            "group.id": config["group_id"],
            "auto.offset.reset": "earliest",
            "enable.auto.commit": True
        })
        self.topic = config["topic"]
        self.handler = handler

    def start(self):
        self.consumer.subscribe([self.topic])
        logger.info(f"Kafka Consumer listening on topic: {self.topic}")

        try:
            while True:
                msg = self.consumer.poll(1.0)
                if msg is None:
                    continue
                if msg.error():
                    raise KafkaException(msg.error())
                data = json.loads(msg.value().decode("utf-8"))
                self.handler.process_event(data)
        except KeyboardInterrupt:
            logger.info("Kafka consumer stopped manually")
        finally:
            self.consumer.close()
