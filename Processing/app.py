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
from sqlalchemy import desc
from stats import UnifiedStats
import uuid
from connexion.middleware import MiddlewarePosition
from starlette.middleware.cors import CORSMiddleware
from connexion import FlaskApp
import os
import sqlite3
from initialize_db import initialize_database

if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_conf.yml"
    log_conf_file = "/config/log_conf.yml"
else:
    print("In Dev Environment")
    app_conf_file = "app_conf.yml"
    log_conf_file = "log_conf.yml"

# Load configuration
with open(log_conf_file, 'r') as f:
    log_config = yaml.safe_load(f)

logging.config.dictConfig(log_config)
logger = logging.getLogger('basicLogger')

with open(app_conf_file, 'r') as f:
    app_config = yaml.safe_load(f.read())

# Initialize the database
initialize_database(app_config)

# Create SQLAlchemy engine and session
engine = create_engine(f"sqlite:///{app_config['datastore']['filename']}")
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)


def populate_stats():
    logger.info("----------------------------------------------------")
    session = DBSession()
 
    # Get or create the unified stats record
    unified_stats = session.query(UnifiedStats).first()
    if not unified_stats:
        unified_stats = UnifiedStats(
            num_health_metrics=0,
            max_heart_rate=0,
            total_calories_burned=0,
            num_workout_events=0,
            total_duration=0,
            last_updated=datetime.datetime.utcnow()
        )
        session.add(unified_stats)

    try:
        current_datetime = datetime.datetime.utcnow()
        last_updated_time = unified_stats.last_updated if unified_stats.last_updated else current_datetime
        last_updated_str = last_updated_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        current_datetime_str = current_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")

        
        # Update your endpoints to use the correct start and end timestamps
        health_metrics_endpoint = f"http://microservices-3855.eastus.cloudapp.azure.com:8090/healthMetrics?start_timestamp={last_updated_str}&end_timestamp={current_datetime_str}"
        workout_events_endpoint = f"http://microservices-3855.eastus.cloudapp.azure.com:8090/workoutEvents?start_timestamp={last_updated_str}&end_timestamp={current_datetime_str}"

   

        # Fetch new workout events
        workout_events_response = requests.get(workout_events_endpoint, params={'start_timestamp': last_updated_str})
        logger.info(f"******workout_events_response: {workout_events_response} from {workout_events_endpoint}")

        if workout_events_response.status_code == 200:
            workout_events_data = workout_events_response.json()
            if workout_events_data:
                for event in workout_events_data:
                        unified_stats.num_workout_events += 1
                        logger.info('-------workout event trace id: %s', event.get('trace_id', 'N/A'))
                        unified_stats.total_duration += event.get('duration', 0)

        # Fetch new health metrics
        health_metrics_response = requests.get(health_metrics_endpoint, params={'start_timestamp': last_updated_str})
        if health_metrics_response.status_code == 200:
            health_metrics_data = health_metrics_response.json()
            if health_metrics_data:
                logger.info(f"******health_metrics_response: {health_metrics_response} from {health_metrics_endpoint}")
                for metric in health_metrics_data:
                            unified_stats.num_health_metrics += 1
                            logger.info('----------health metrics trace id: %s', metric.get('trace_id', 'N/A'))

                            unified_stats.total_calories_burned += metric.get('caloriesBurned', 0)
                            unified_stats.max_heart_rate = max(unified_stats.max_heart_rate, metric.get('heartRate', 0))

        # Update the last_updated timestamp only if new data was received
        if health_metrics_data or workout_events_data:
            unified_stats.last_updated = current_datetime

        # Update the last_updated timestamp

        session.commit()
        logger.info(f"Updated stats: {unified_stats.to_dict()}")
    except Exception as e:
        logger.error(f"Error in periodic processing: {str(e)}")
        session.rollback()
    finally:
        session.close()
    logger.info("Periodic Processing Ended")


def get_stats():
    logger.info("GET stats request has started")
    session = DBSession()
    try:
        unified_stats = session.query(UnifiedStats).order_by(UnifiedStats.last_updated.desc()).first()
        
        if not unified_stats:
            logger.error("Statistics do not exist")
            return {"message": "Statistics do not exist"}, 404

        stats_dict = unified_stats.to_dict()

        logger.debug(f"Returning stats: {stats_dict}")
    except Exception as e:
        session.rollback()
        logger.error(f"Error retrieving statistics: {str(e)}")
        return {"message": "Error retrieving statistics"}, 500
    finally:
        session.close()

    logger.info("GET stats request has completed")
    return stats_dict, 200

# Schedule the periodic processing
def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats, 'interval', seconds=app_config['scheduler']['period_sec'])
    sched.start()

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
    init_scheduler()
    app.run(host='0.0.0.0', port=8100)



