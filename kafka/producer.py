from confluent_kafka import Producer, KafkaException
import json
from loguru import logger


class KafkaProducerService:
    def __init__(self, config):
        """
        Kafka Producer 초기화
        :param config: {
            "bootstrap_servers": "localhost:9092",
            "topic": "example-topic"
        }
        """
        self.producer = Producer({
            "bootstrap.servers": config["bootstrap_servers"]
        })
        self.topic = config["topic"]

    def delivery_report(self, err, msg):
        """Kafka 전송 결과 콜백"""
        if err is not None:
            logger.error(f"Message delivery failed: {err}")
        else:
            logger.info(
                f"Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}"
            )

    def produce(self, data):
        """
        Kafka 토픽으로 메시지를 전송
        :param data: dict 형태의 데이터 (자동으로 JSON 직렬화됨)
        """
        try:
            message = json.dumps(data).encode("utf-8")
            self.producer.produce(
                topic=self.topic,
                value=message,
                callback=self.delivery_report
            )
            # 내부 버퍼에 쌓인 메시지를 전송
            self.producer.poll(0)
        except BufferError:
            logger.error("Local producer queue is full — try again later.")
        except KafkaException as e:
            logger.error(f"Kafka exception occurred: {e}")
        except Exception as e:
            logger.exception(f"Unexpected error producing message: {e}")

    def flush(self):
        """남아있는 메시지 전송 후 종료"""
        logger.info("Flushing pending messages...")
        self.producer.flush()
        logger.info("All messages flushed and producer closed.")


# 사용 예시
if __name__ == "__main__":
    config = {
        "bootstrap_servers": "localhost:9092",
        "topic": "test-topic"
    }

    producer = KafkaProducerService(config)
    try:
        producer.produce({"event": "user_signup", "user_id": 123})
        producer.produce({"event": "order_created", "order_id": 456})
    finally:
        producer.flush()
