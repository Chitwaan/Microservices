import connexion
from connexion import NoContent
import yaml
import logging.config
import uuid
from pykafka import KafkaClient
import json
from datetime import datetime

# Load configuration files
with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f)
logging.config.dictConfig(log_config)

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f)

logger = logging.getLogger('basicLogger')

# Kafka configuration
kafka_config = app_config['events']
kafka_client = KafkaClient(hosts=f"{kafka_config['hostname']}:{kafka_config['port']}")
kafka_topic = kafka_client.topics[str.encode(kafka_config['topic'])]
kafka_producer = kafka_topic.get_sync_producer()

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

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(port=8080)
