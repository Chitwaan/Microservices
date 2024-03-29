import connexion
from connexion import NoContent
import yaml
import logging.config
import uuid
from pykafka import KafkaClient
import json
from datetime import datetime
import time


def initialize_kafka_producer_with_retry(kafka_config, max_retries=5, retry_wait=3):
    """Initialize Kafka producer with retry logic."""
    retry_count = 0
    while retry_count < max_retries:
        try:
            logger.info('Attempting to connect to Kafka...')
            kafka_client = KafkaClient(hosts=f"{kafka_config['hostname']}:{kafka_config['port']}")
            kafka_topic = kafka_client.topics[str.encode(kafka_config['topic'])]
            kafka_producer = kafka_topic.get_sync_producer()
            logger.info('Successfully connected to Kafka')
            return kafka_producer
        except Exception as e:
            logger.error(f"Failed to connect to Kafka on retry {retry_count}: {e}")
            time.sleep(retry_wait)
            retry_count += 1
    raise Exception("Failed to initialize Kafka producer after max retries")

# Load configuration files
with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f)
logging.config.dictConfig(log_config)

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f)

logger = logging.getLogger('basicLogger')

kafka_producer = initialize_kafka_producer_with_retry(app_config['events'])

# Kafka configuration
# kafka_config = app_config['events']
# logger.info('kafka starting')
# kafka_client = KafkaClient(hosts=f"{kafka_config['hostname']}:{kafka_config['port']}")
# logger.info('kafka done')
# kafka_topic = kafka_client.topics[str.encode(kafka_config['topic'])]
# kafka_producer = kafka_topic.get_sync_producer()

def postWorkoutData(body):
    trace_id = str(uuid.uuid4())
    msg = {
        "type": 'workout event',
        "datetime": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S"),
        "payload": body,
        "trace_id": trace_id
    }
    msg_str = json.dumps(msg)
    kafka_producer.produce(msg_str.encode('utf-8'))
    logger.info(f"Produced workout event message with trace id: {trace_id}")
    return NoContent, 201

def postHealthMetrics(body):
    trace_id = str(uuid.uuid4())
    msg = {
        "type": 'health metrics',
        "datetime": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S"),
        "payload": body,
        "trace_id": trace_id
    }
    msg_str = json.dumps(msg)
    kafka_producer.produce(msg_str.encode('utf-8'))
    logger.info(f"Produced health metrics message with trace id: {trace_id}")
    return NoContent, 201


def send_startup_message():
    """Send a message indicating the receiver service is ready."""
    message = {
        "type": "service status",
        "datetime": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S"),
        "service": "Receiver",
        "status": "ready",
        "code": "0001",
        "description": "Receiver service has started and is ready to receive messages."
    }
    msg_str = json.dumps(message)
    kafka_producer.produce(msg_str.encode('utf-8'))
    logger.info("Sent service ready message to Kafka.")


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    # send_startup_message() 
    app.run(host='0.0.0.0', port=8080)
