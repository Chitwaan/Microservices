import connexion
from connexion import NoContent

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import connexion
from connexion import NoContent
import json
from datetime import datetime
from sqlalchemy import func
import yaml
from flask import request
from connexion.middleware import MiddlewarePosition
from starlette.middleware.cors import CORSMiddleware
import logging
import logging.config
from sqlalchemy import and_
from threading import Thread
from pykafka import KafkaClient
from pykafka.common import OffsetType
import time
from models.event_log import init_db, EventLog


with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f)

logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

db_session = init_db(f"sqlite:///{app_config['database']['filename']}")


def consume_events():
    max_retries = app_config['kafka']['max_retries']
    retry_wait = app_config['kafka']['retry_wait'] 
    retry_count = 0
    while retry_count < max_retries:
        try:
            client = KafkaClient(hosts=f"{app_config['events']['hostname']}:{app_config['events']['port']}")
            topic = client.topics[str.encode(app_config['events']['topic'])]
            consumer = topic.get_simple_consumer()
            logger.info("Successfully connected to Kafka")
            break
        except Exception as e:
            logger.error(f"Failed to connect to Kafka on retry {retry_count}: {e}")
            time.sleep(retry_wait)
            retry_count += 1
    if retry_count == max_retries:
        logger.error("Max retries reached. Failed to connect to Kafka.")
        return  # Exit function if connection fails after retries
    for message in consumer:
        if message is not None:
            msg_data = json.loads(message.value.decode('utf-8'))
            
            # Enhanced filtering based on 'code' value to include all service types
            if msg_data.get('type') in ["service status", "Processing Exceeded"] and msg_data.get('code') in ["0001", "0002", "0003", "0004"]:
                # Map service names to codes for more accurate logging
                service_map = {
                    "0001": "Receiver",
                    "0002": "Storage",
                    "0003": "Processor",
                    "0004": "Processing Exceeded Notification"
                }
                service = service_map.get(msg_data.get('code'), "Unknown Service")
                logger.info(f"Consumed message for {service}: {msg_data}")

                # Process the message
                event_log = EventLog(
                    message=msg_data.get('message', 'No description'),
                    code=msg_data.get('code', 'No code')
                )
                db_session.add(event_log)
                db_session.commit()




def get_event_stats():
    stats = db_session.query(EventLog.code, func.count(EventLog.code).label("count")).group_by(EventLog.code).all()
    return {code: count for code, count in stats}


app = connexion.FlaskApp(__name__, specification_dir='')

app.add_middleware(
    CORSMiddleware,
    position=MiddlewarePosition.BEFORE_EXCEPTION,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)


if __name__ == "__main__":
    consumer_thread = Thread(target=consume_events, daemon=True)
    consumer_thread.start()
    app.run(host='0.0.0.0', port=8120)
