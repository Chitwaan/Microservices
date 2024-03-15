from flask import Flask
import connexion
from pykafka import KafkaClient
import json
import yaml
import logging.config
from connexion.middleware import MiddlewarePosition
from starlette.middleware.cors import CORSMiddleware
from connexion import FlaskApp

# Load configuration
with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

# logging
with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')



logger.info(f"Kafka server: {app_config['events']['hostname']}:{app_config['events']['port']}")

def get_event_by_index(index, event_type):
    """Generic function to retrieve an event by index from Kafka, filtering by event type."""
    try:
        client = KafkaClient(hosts=f"{app_config['events']['hostname']}:{app_config['events']['port']}")
        topic = client.topics[str.encode(app_config['events']['topic'])]
        consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=1000)
        
        logger.info(f"Attempting to retrieve {event_type} event at index {index}")
        
        filtered_index = 0
        for msg in consumer:
            if msg is not None:
                msg_dict = json.loads(msg.value.decode('utf-8'))
                if msg_dict["type"] == event_type:
                    if filtered_index == index:
                        logger.info(f"Found and returning {event_type} event at filtered index {filtered_index}")
                        return msg_dict['payload'], 200  
                    filtered_index += 1
                
        logger.error(f"Could not find {event_type} event at index {index}")
        return {"message": "Not Found"}, 404
        
    except RuntimeError as e:
        if str(e) == 'generator raised StopIteration':
            logger.info(f"No more messages found in topic for {event_type} at index {index}")
            return {"message": "Not Found"}, 404
        else:
            logger.error(f"Unexpected RuntimeError retrieving {event_type} event at index {index}: {str(e)}", exc_info=True)
            return {"message": "Internal Server Error"}, 500
    except Exception as e:
        logger.error(f"Error retrieving {event_type} event at index {index}: {str(e)}", exc_info=True)
        return {"message": "Internal Server Error"}, 500
    
def get_workout_event_by_index(index):
    """Retrieve a workout event by index"""
    return get_event_by_index(index, 'workout event')

def get_health_metrics_by_index(index):
    """Retrieve a health metric by index"""
    return get_event_by_index(index, 'health metrics')

app = connexion.FlaskApp(__name__, specification_dir='')

app.add_middleware(
    CORSMiddleware,
    position=MiddlewarePosition.BEFORE_EXCEPTION,
    allow_origins=["*"],  # For development, you can allow all origins. Adjust for production!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_api('openapi.yml',  strict_validation=True, validate_responses=True)

if __name__ == '__main__':
    port = 8110
    logger.info(f"Starting server on port {port}")
    app.run( host='0.0.0.0', port=port)
    logger.info(f"Server is running on port {port}")
