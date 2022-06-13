import logging
import traceback

from Logger.CustomLogFormatter import CustomLogFormatter
from RabbitMq.Query import ResultResponse
from RabbitMq.RabbitMQClient import RabbitMQProducer, RabbitMQSyncConsumer, RabbitMQAsyncConsumer
from SimilarThingsFilter.SimilarThingsFilter import process_request
from Utils.Utils import setup_health_consumer

logger = logging.getLogger("SimilarThingsFilterConsumer")
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(CustomLogFormatter())
logger.addHandler(ch)

SERVICE_NAME = "things_service"

if __name__ == '__main__':
    logger.info("Starting SimilarThingsFilterConsumer")
    consumer = RabbitMQSyncConsumer.from_config('similar_things')
    producer = RabbitMQProducer.from_config()
    health_consumer = RabbitMQAsyncConsumer.from_config('health')
    logger.info("SimilarThingsFilterConsumer started successfully")

    logger.info("Starting HealthConsumer")
    setup_health_consumer(SERVICE_NAME, producer, health_consumer)
    logger.info("HealthConsumer started successfully")

    def callback(ch, method, properties, body):
        logger.info(" [x] Received %r" % body)
        try:
            result = process_request(body)
            resp = ResultResponse(200, result, SERVICE_NAME)
        except Exception as e:
            logging.error(traceback.format_exc())
            resp = ResultResponse(500, [], SERVICE_NAME)
        producer.publish_rmq_message(resp)

    consumer.consume(callback)
