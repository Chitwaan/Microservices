from sqlalchemy import Column, Integer, DateTime, create_engine, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

Base = declarative_base()

class UnifiedStats(Base):
    """Unified statistics for health metrics and workout events."""
    __tablename__ = 'unified_stats'
    
    id = Column(Integer, primary_key=True)
    num_health_metrics = Column(Integer, default=0)
    max_heart_rate = Column(Integer, default=0)
    total_calories_burned = Column(Integer, default=0)
    num_workout_events = Column(Integer, default=0)
    total_duration = Column(Integer, default=0)
    last_updated = Column(DateTime, default=datetime.datetime.now())
    
    def to_dict(self):
        return {
            'num_health_metrics': self.num_health_metrics,
            'max_heart_rate': self.max_heart_rate,
            'total_calories_burned': self.total_calories_burned,
            'num_workout_events': self.num_workout_events,
            'total_duration': self.total_duration,
            'last_updated': self.last_updated.strftime("%Y-%m-%dT%H:%M:%SZ")
        }

