from redis import Redis
from rq import Queue
import os

redis_connection = Redis(host=os.getenv("REDIS_HOSTNAME"),
                         port=os.getenv("REDIS_PORT"),
                         db=0)
worker_queue = Queue(os.getenv("REDIS_QUEUE"), connection=redis_connection)
