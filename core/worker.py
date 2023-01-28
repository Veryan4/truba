#!/usr/bin/env python
import redis
from rq import Worker, Queue, Connection
import os

from shared import *
from shared.types import *
from services.search import *
from services.story import *
from services.user import *
from services import *

# Provide queue names to listen to as arguments to this script,
# similar to rq worker

redis_url = "redis://" + os.getenv("REDIS_HOSTNAME") + ":" + os.getenv(
    "REDIS_PORT")
conn = redis.from_url(redis_url)
listen = [os.getenv("REDIS_QUEUE")]

with Connection(conn):
  worker = Worker(list(map(Queue, listen)))
  worker.work()
