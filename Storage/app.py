import connexion
from connexion import NoContent

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base
import connexion
from connexion import NoContent
import json
from datetime import datetime
from health_metrics import HealthMetric
import uuid
import yaml
from flask import request
from workout_events import WorkoutEvent
import logging
import logging.config
from sqlalchemy import and_
from threading import Thread
from pykafka import KafkaClient
from pykafka.common import OffsetType



with open('storage_log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f)

logging.config.dictConfig(log_config)

logger = logging.getLogger('storageLogger')

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

db_config = app_config['database']  
engine_url = f"mysql+pymysql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['dbname']}"


DB_ENGINE = create_engine(engine_url)
DB_SESSION = sessionmaker(bind=DB_ENGINE)
logging.info("Connecting to MySQL database at hostname: %s, port: %s", "microservices-3855.eastus.cloudapp.azure.com", 3306)



def postWorkoutData(body):
    session = DB_SESSION()
    trace_id = body.get('trace_id', 'default_trace_id')

    logger.info(f"Received workout event request with a trace id of {trace_id}")
    try:
        workout_event = WorkoutEvent(
            user_device_id=body['userDeviceId'],
            exercise_type=body['exerciseType'],
            duration=body['duration'],
            intensity=body['intensity'],
            trace_id=trace_id
        )
        session.add(workout_event)
        session.commit()
        return NoContent, 201

    except Exception as e:
        session.rollback()
        logger.error(f"Error processing workout event with trace id {trace_id}: {str(e)}")

        raise e
    finally:
        session.close()



def postHealthMetrics(body):
    session = DB_SESSION()   
    # trace_id = body['trace_id'] 
    trace_id = body.get('trace_id', 'default_trace_id')

    logger.info(f"Received health metrics request with a trace id of {trace_id}")

    try:
        health_metric = HealthMetric(
            user_device_id=body['userDeviceId'],
            heart_rate=body['heartRate'],
            calories_burned=body['caloriesBurned'],
            trace_id=trace_id
        )
        
        session.add(health_metric)
        session.commit()
        return f"Heart rate {body['heartRate']}, burned {body['caloriesBurned']} calories", 201
        
    except Exception as e:
        session.rollback()
        logger.error(f"Error processing health metrics with trace id {trace_id}: {str(e)}")

        raise e
    finally:
        session.close()

def process_messages():
    """ Process event messages from Kafka """
    hostname = f"{app_config['events']['hostname']}:{app_config['events']['port']}"
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config['events']['topic'])]
    consumer = topic.get_simple_consumer(consumer_group=b'event_group',
                                         reset_offset_on_start=False,
                                         auto_offset_reset=OffsetType.LATEST)
    
    for msg in consumer:
        if msg is not None:
            try:
                msg_str = msg.value.decode('utf-8')
                msg_dict = json.loads(msg_str)
                logger.info(f"Message: {msg_dict}")
                
                trace_id = msg_dict.get('trace_id', 'default_trace_id')

                payload = msg_dict["payload"]
                payload['trace_id'] = trace_id  

                if msg_dict["type"] == "workout event":
                    postWorkoutData(payload)
                elif msg_dict["type"] == "health metrics":
                    postHealthMetrics(payload)
                
                consumer.commit_offsets()
            except Exception as e:
                logger.error(f"Error processing message: {e}")

        
def getWorkoutEventsByTimeRange(start_timestamp, end_timestamp):
    session = DB_SESSION()
    logger.info(f"*****Received request for workout with start_timestamp")

    start_timestamp = request.args.get('start_timestamp')
    end_timestamp = request.args.get('end_timestamp')
    logger.info(f"Received request for getWorkoutEventsByTimeRange with start_timestamp={start_timestamp} and end_timestamp={end_timestamp}")

    start_datetime = datetime.strptime(start_timestamp, "%Y-%m-%dT%H:%M:%SZ")
    end_datetime = datetime.strptime(end_timestamp, "%Y-%m-%dT%H:%M:%SZ")

    
    try:
        workout_events = session.query(WorkoutEvent).filter(
            and_(WorkoutEvent.date_created >= start_datetime, WorkoutEvent.date_created < end_datetime)
        ).all()

        workout_events_data = [event.to_dict() for event in workout_events]
        logger.info(f"Found {len(workout_events_data)} workout events")
        return workout_events_data, 200
    except Exception as e:
        logger.error(f"Error retrieving workout events: {str(e)}")
        return {"message": "Error retrieving workout events"}, 500
    finally:
        session.close()

      

def getHealthMetricsByTimeRange(start_timestamp, end_timestamp):
    session = DB_SESSION()
    start_timestamp = request.args.get('start_timestamp')
    end_timestamp = request.args.get('end_timestamp')
    logger.info(f"Received request for getHealthMetricsByTimeRange with start_timestamp={start_timestamp} and end_timestamp={end_timestamp}")

    # Convert start and end timestamps to datetime objects
    start_datetime = datetime.strptime(start_timestamp, "%Y-%m-%dT%H:%M:%SZ")
    end_datetime = datetime.strptime(end_timestamp, "%Y-%m-%dT%H:%M:%SZ")

    try:
        # Query HealthMetric objects within the given datetime range
        health_metrics = session.query(HealthMetric).filter(
            and_(HealthMetric.date_created >= start_datetime, HealthMetric.date_created < end_datetime)
        ).all()

        # Convert queried HealthMetric objects to dictionaries
        health_metrics_data = [metric.to_dict() for metric in health_metrics]
        logger.info(f"Found {len(health_metrics_data)} health metrics")
        return health_metrics_data, 200
    except Exception as e:
        logger.error(f"Error retrieving health metrics: {str(e)}")
        session.rollback()  # Ensure the session rollback in case of an error
        return {"message": "Error retrieving health metrics"}, 500
    finally:
        session.close()

    return health_metrics_data, 200

# def getHealthMetricsByTimeRange(start_timestamp, end_timestamp):
#         session = DB_SESSION()
#         start_datetime = datetime.datetime.strptime(start_timestamp, "%Y-%m-%dT%H:%M:%S")
#         end_datetime = datetime.datetime.strptime(end_timestamp, "%Y-%m-%dT%H:%M:%S")


#         logger.info(f"Received request for getHealthMetricsByTimeRange with start_timestamp={start_timestamp} and end_timestamp={end_timestamp}")
  
#         logger.info(f"$$Querying health metrics with start_datetime={start_datetime} and end_datetime={end_datetime}")

    
#         try:
#             logger.info(f"##Querying health metrics with start_datetime={start_datetime} and end_datetime={end_datetime}")
#             health_metrics = session.query(HealthMetric).filter(
#                 and_(HealthMetric.date_created >= start_datetime, HealthMetric.date_created <= end_datetime)
#             ).all()

#             health_metrics_data = [metric.to_dict() for metric in health_metrics]
#             logger.info(f"Found {len(health_metrics_data)} health metrics")

#             return health_metrics_data, 200
#         except Exception as e:
#             logger.error(f"Error retrieving health metrics: {str(e)}")
#             return {"message": "Error retrieving health metrics"}, 500
#         finally:
#             session.close()




app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    t1 = Thread(target=process_messages)
    t1.daemon =True
    t1.start()
    app.run(port=8090)


