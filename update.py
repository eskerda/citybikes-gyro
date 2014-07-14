import argparse

from redis import Redis, ConnectionPool
from rq import Queue

from gyro import tasks
from gyro.configuration import redis_server as redis_info
from gyro.configuration import ignore as ignored_services
import pybikes
import keys

def enqueueUniSystem(queue, task, instances, key, network = None):
    for instance in instances:
        if network is None or network == instance['tag']:
            print "Putting %s on an %s queue!" % (instance['tag'], str(task))
            queue.enqueue(task, schema['system'], instance['tag'], key)

def enqueueMultiSystem(queue, task, schema, key, network = None):
    for cls in schema['class']:
        enqueueUniSystem(queue, task, schema['class'][cls]['instances'], key, network)

pool = ConnectionPool(
    host=redis_info['host'],
    port=redis_info['port'],
    db=redis_info['db']
)

q = Queue('medium', connection=Redis(connection_pool = pool))

parser = argparse.ArgumentParser(description='Process bike sharing networks')
parser.add_argument('--schema', help = 'selected bike sharing scheme',
                   default=None)
parser.add_argument('--network', help = 'a network in the bike sharing scheme',
                   default=None)
parser.add_argument('--sync', help = 'resync network! (Dangerous, Alarm!)',
                   default=False, action = 'store_true')
args = parser.parse_args()

if args.schema is None:
    schema_files = pybikes.getDataFiles()
    schemas = [pybikes.getDataFile(f) for f in schema_files]
else:
    schemas = [pybikes.getDataFile(args.schema)]

if args.sync:
    task = tasks.syncSystem
else:
    task = tasks.updateSystem

for schema in schemas:
    if schema['system'] in ignored_services:
        print "Ignoring %s !!1one" % schema['system']
        continue
    if hasattr(keys, schema['system']):
        key = eval('keys.%s' % schema['system'])
    else:
        key = None

    if isinstance(schema['class'], unicode):
        enqueueUniSystem(q, task, schema['instances'], key, args.network)
    elif isinstance(schema['class'], dict):
        enqueueMultiSystem(q, task, schema, key, args.network)
    else:
        raise Exception('Malformed schema')

