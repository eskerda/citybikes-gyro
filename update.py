from redis import Redis, ConnectionPool
from rq import Queue
from gyro import tasks
from gyro.configuration import redis_server as redis_info
import pybikes

pool = ConnectionPool(host=redis_info['host'],port=redis_info['port'],db=0)
q = Queue('medium', connection=Redis(connection_pool = pool))

schema_files = pybikes.getDataFiles()
schemas = [pybikes.getDataFile(f) for f in schema_files]
for schema in schemas:
    for instance in schema['instances']:
        q.enqueue(tasks.updateSystem, schema['system'], instance['tag'])