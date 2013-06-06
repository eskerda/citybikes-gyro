import argparse

from redis import Redis, ConnectionPool
from rq import Queue

from gyro import tasks
from gyro.configuration import redis_server as redis_info
import pybikes

pool = ConnectionPool(host=redis_info['host'],port=redis_info['port'],db=0)
q = Queue('medium', connection=Redis(connection_pool = pool))

parser = argparse.ArgumentParser(description='Process bike sharing networks')
parser.add_argument('--schema', help = 'selected bike sharing scheme',
                   default=None)
parser.add_argument('--network', help = 'a network in the bike sharing scheme',
                   default=None)
args = parser.parse_args()

if args.schema is None:
    schema_files = pybikes.getDataFiles()
    schemas = [pybikes.getDataFile(f) for f in schema_files]
else:
    schemas = [pybikes.getDataFile(args.schema)]


for schema in schemas:
    for instance in schema['instances']:
        if args.network is None or args.network == instance['tag']:
            print "Putting %s on an update queue!" % instance['tag']
            q.enqueue(tasks.updateSystem, schema['system'], instance['tag'])
