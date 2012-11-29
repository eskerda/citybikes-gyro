from redis import Redis
from rq import Queue
from gyro import tasks
import pybikes

q = Queue(connection=Redis())

schema_files = pybikes.getDataFiles()
schemas = [pybikes.getDataFile(f) for f in schema_files]
for schema in schemas:
    for instance in schema['instances']:
        q.enqueue(tasks.updateSystem, schema['system'], instance['tag'])