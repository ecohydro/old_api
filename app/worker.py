import os
import redis
from redis import Redis
import urlparse
from flask import current_app as app

from rq import Worker, Queue, Connection

listen = ['high', 'default', 'low']

urlparse.uses_netloc.append('redis')
url = urlparse.urlparse(str(os.getenv('REDISTOGO_URL')).replace("'",""))
conn = Redis(host=url.hostname, port=url.port, db=0, password=url.password)

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()

