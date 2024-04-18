from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
class Anomaly(Base):
    """Anomaly record for events that exceed specified thresholds."""
    __tablename__ = 'anomaly'

    id = Column(Integer, primary_key=True)
    event_id = Column(String(250), nullable=False)
    trace_id = Column(String(250), nullable=False)
    event_type = Column(String(100), nullable=False)
    anomaly_type = Column(String(100), nullable=False)
    description = Column(String(250), nullable=False)
    date_created = Column(DateTime, default=datetime.datetime.utcnow)

    def __init__(self, event_id, trace_id, event_type, anomaly_type, description):
        self.event_id = event_id
        self.trace_id = trace_id
        self.event_type = event_type
        self.anomaly_type = anomaly_type
        self.description = description

    def to_dict(self):
        return {
            'id': self.id,
            'event_id': self.event_id,
            'trace_id': self.trace_id,
            'event_type': self.event_type,
            'anomaly_type': self.anomaly_type,
            'description': self.description,
            'date_created': self.date_created.isoformat()
        }
