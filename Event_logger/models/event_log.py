from sqlalchemy import create_engine, Column, String, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

Base = declarative_base()

class EventLog(Base):
    __tablename__ = "event_log"
    id  = Column(Integer, primary_key=True)
    message = Column(String)
    code = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

def init_db(uri):
    engine = create_engine(uri)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()