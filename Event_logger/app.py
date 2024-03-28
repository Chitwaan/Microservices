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

import logging
import logging.config
from sqlalchemy import and_
from threading import Thread
from pykafka import KafkaClient
from pykafka.common import OffsetType
import time
from models.event_log import init_db, EventLog


with open('storage_log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f)

logging.config.dictConfig(log_config)

logger = logging.getLogger('storageLogger')

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

db_session = init_db(f"sqlite:///{app_config['database']['filename']}")


def consume_events():
    client = KafkaClient(hosts=f"{app_config['events']['hostname']}:{app_config['events']['port']}")
    topic = client.topics[str.encode(app_config['events']['topic'])]  
    consumer = topic.get_simple_consumer()


    client = KafkaClient(hosts=f"{app_config['events']['hostname']}:{app_config['events']['port']}")
    topic = client.topics[str.encode(app_config['events']['topic'])]  
    for message in consumer:
        if message is not None:
            msg_data = json.loads(message.value.decode('utf-8'))
            logger.info(f"Consumed message: {msg_data}")

            event_log = EventLog(
                message=msg_data['message'],
                code=msg_data['code']
            )
            db_session.add(event_log)
            db_session.commit()



def get_event_stats():
    stats = db_session.query(EventLog.code, func.count(EventLog.code).label("count")).group_by(EventLog.code).all()
    return {code: count for code, count in stats}


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)


if __name__ == "__main__":
    consumer_thread = Thread(target=consume_events, daemon=True)
    consumer_thread.start()
    app.run(host='0.0.0.0', port=8120)
