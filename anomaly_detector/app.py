from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base
# from stats import stats
import yaml
import logging
import logging.config
from apscheduler.schedulers.background import BackgroundScheduler
import datetime
import connexion
import requests
# from kafka import KafkaConsumer

from sqlalchemy import desc
import uuid, json
from connexion.middleware import MiddlewarePosition
from starlette.middleware.cors import CORSMiddleware
from connexion import FlaskApp
import os
import sqlite3, time
from pykafka import KafkaClient
from models import Anomaly
from flask import jsonify


with open("log_conf.yml", 'r') as f:
    log_config = yaml.safe_load(f)

logging.config.dictConfig(log_config)
logger = logging.getLogger('basicLogger')

with open("app_conf.yml", 'r') as f:
    logger.info("app_conf.yml")
    app_config = yaml.safe_load(f.read())


engine = create_engine(f"sqlite:///{app_config['database']['filepath']}")
Base.metadata.bind = engine
Session = sessionmaker(bind=engine)

def initialize_kafka_producer_with_retry(kafka_config, max_retries=5, retry_wait=3):
    """Initialize Kafka producer with retry logic."""
    retry_count = 0
    while retry_count < max_retries:
        try:
            logger.info('Attempting to connect to Kafka.....')
            kafka_client = KafkaClient(hosts=f"{kafka_config['hostname']}:{kafka_config['port']}")
            kafka_topic = kafka_client.topics[str.encode(kafka_config['topic'])]
            kafka_producer = kafka_topic.get_sync_producer()
            logger.info('Successfully connected to Kafka')
            return kafka_producer
        except Exception as e:
            logger.error(f"Failed to connect to Kafka on retry {retry_count}: {e}")
            time.sleep(retry_wait)
            retry_count += 1
    logger.error("Failed to initialize Kafka producer after max retries...")
    return None



# # Kafka Consumer setup
# consumer = KafkaConsumer(
#     app_config['events']['topic'],
#     bootstrap_servers=[f"{app_config['events']['hostname']}:{app_config['events']['port']}"],
#     auto_offset_reset='earliest',
#     enable_auto_commit=True,
#     value_deserializer=lambda x: json.loads(x.decode('utf-8'))
# )

client = KafkaClient(hosts=f"{app_config['events']['hostname']}:{app_config['events']['port']}")
topic = client.topics[str.encode(app_config['events']['topic'])]
consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=1000)


def check_for_anomalies(data):
    """ Checks incoming Kafka messages for anomalies. """
    anomalies = []
    thresholds = app_config['thresholds']
    
    for key, threshold in thresholds.items():
        if key in data['payload'] and (data['payload'][key] < threshold['min'] or data['payload'][key] > threshold['max']):
            anomaly = Anomaly(
                event_id=data['payload']['userDeviceId'], 
                trace_id=data['trace_id'],
                event_type=data['type'],
                anomaly_type='Too High' if data['payload'][key] > threshold['max'] else 'Too Low',
                description=f"{key} of {data['payload'][key]} is outside the threshold range {threshold}",

                date_created=datetime.datetime.utcnow()
            )
            anomalies.append(anomaly)
            logger.info(f"Anomaly detected: {anomaly.to_dict()}")
    return anomalies


def process_messages():
    session = Session()
    for message in consumer:
        logger.info(f"Received message: {message.value}")
        anomalies = check_for_anomalies(message.value)
        for anomaly in anomalies:
            session.add(anomaly)
        session.commit()
    session.close()

def get_anomalies():
    """ API Endpoint to fetch anomalies. """
    session = Session()
    anomalies_query = session.query(Anomaly).all()
    if not anomalies_query:
        return jsonify({'message': 'Anomalies do not exist'}), 404
    results = [anom.to_dict() for anom in anomalies_query]
    session.close()
    return jsonify(results), 200



kafka_producer = initialize_kafka_producer_with_retry(app_config['events'])
app = connexion.FlaskApp(__name__, specification_dir='./')

# Add a Flask API
app.add_api('openapi1.yaml', strict_validation=True, validate_responses=True)
flask_app = app.app  # This is your underlying Flask app instance in Connexion

# app = connexion.FlaskApp(__name__, specification_dir='')
# app.add_api("openapi1.yaml", strict_validation=True, validate_responses=True)

if __name__ == '__main__':
    flask_app.run(debug=True, port=5000)