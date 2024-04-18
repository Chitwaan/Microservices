from sqlalchemy import create_engine, Column, String, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

Base = declarative_base()

class EventLog(Base):
    """
    A declarative base model for the EventLog table.
    
    Attributes:
        id (Integer): The primary key.
        message (String): The log message.
        code (String): A code associated with the log message.
        created_at (DateTime): The timestamp when the log was created, defaulting to the current UTC time.
    """
    __tablename__ = "event_log"
    id  = Column(Integer, primary_key=True)
    message = Column(String)
    code = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

def init_db(uri):
    """
    Initializes the database by creating tables based on declarative base models and returns a session maker instance.
    
    Args:
        uri (str): The database connection URI.
    
    Returns:
        session: A session maker instance bound to the engine.
    """
    engine = create_engine(uri)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()