from sqlalchemy import create_engine
from base import Base
from models import Anomaly

def create_database(database_url='sqlite:///anomaly_detector.db'):
    engine = create_engine(database_url, echo=True)
    Base.metadata.create_all(engine)

if __name__ == '__main__':
    create_database()
