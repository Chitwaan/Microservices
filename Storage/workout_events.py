from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql.functions import now
from base import Base
import datetime
from datetime import datetime

class WorkoutEvent(Base):
    """ Workout Event """

    __tablename__ = "workout_events"

    id = Column(Integer, primary_key=True)
    user_device_id = Column(String(250), nullable=False)
    exercise_type = Column(String(250), nullable=False)
    duration = Column(Integer, nullable=False)
    intensity = Column(String(250), nullable=False)
    date_created = Column(DateTime, nullable=False, default=datetime.now)
    trace_id = Column(String, nullable=True)

    def __init__(self, user_device_id, exercise_type, duration, intensity, trace_id=None):
        """ Initializes a workout event """
        self.user_device_id = user_device_id
        self.exercise_type = exercise_type
        self.duration = duration
        self.intensity = intensity
        self.date_created = datetime.datetime.now() 
        self.trace_id = trace_id

    def to_dict(self):
   
        return {
            'id': self.id,
            'userDeviceId': self.user_device_id,
            'exerciseType': self.exercise_type,
            'duration': self.duration,
            'intensity': self.intensity,
            # 'date_created': self.date_created.strftime("%Y-%m-%dT%H:%M:%S"),
            'trace_id': self.trace_id
        }


