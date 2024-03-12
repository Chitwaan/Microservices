from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql.functions import now
from base import Base
#import datetime
from datetime import datetime

class HealthMetric(Base):
    """ Health Metric """

    __tablename__ = "health_metrics"

    id = Column(Integer, primary_key=True)
    user_device_id = Column(String(250), nullable=False)
    heart_rate = Column(Integer, nullable=False)
    calories_burned = Column(Integer, nullable=False)
    date_created = Column(DateTime, nullable=False, default=datetime.utcnow)
    trace_id = Column(String, nullable=True)

    def __init__(self, user_device_id, heart_rate, calories_burned, trace_id=None):
        """ Initializes a health metric """
        self.user_device_id = user_device_id
        self.heart_rate = heart_rate
        self.calories_burned = calories_burned
        #self.date_created = datetime.datetime.utcnow()  
        self.trace_id = trace_id    


    def to_dict(self):
        """ Dictionary Representation of a health metric """
        return {
            'id': self.id,
            'userDeviceId': self.user_device_id,
            'heartRate': self.heart_rate,
            'caloriesBurned': self.calories_burned,
            # 'date_created': self.date_created.strftime("%Y-%m-%dT%H:%M:%S"),
            'trace_id': self.trace_id
        }

