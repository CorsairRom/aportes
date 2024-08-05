import os
import json
import time
import logging
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base
import redis

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URI = 'postgresql://myuser:mypassword@postgres:5432/mydb'
engine = create_engine(DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()

redis_client = redis.StrictRedis(host='redis', port=6379, decode_responses=True)

Base = declarative_base()

class Data(Base):
    __tablename__ = 'data'
    id = Column(Integer, primary_key=True)
    name = Column(String(150))

    def __init__(self, name):
        self.name = name

def process_task(task):
    try:
        name = task.get('name')
        data = Data(name=name)
        session.add(data)
        time.sleep(0.1)
        session.commit()
        redis_client.rpush('data', json.dumps({'id': data.id, 'name': data.name}))
        logger.info("Processed task: %s", task)
    except Exception as e:
        logger.error("Error processing task: %s - %s", task, e)

def worker():
    logger.info("Worker started")
    while True:
        try:
            task_json = redis_client.lpop('task_queue')
            if task_json:
                task = json.loads(task_json)
                process_task(task)
            else:
                time.sleep(1)
        except Exception as e:
            logger.error("Error in worker loop: %s", e)
            time.sleep(1)

if __name__ == '__main__':
    worker()
