from __future__ import absolute_import
from redis import Redis, ConnectionPool
from rq import Queue
from rq_scheduler import Scheduler
from datetime import timedelta
import pybikes
from gyro.configuration import db_credentials as credentials
from gyro.configuration import redis_server
from pymongo import Connection
from gyro.models import StationDocument, SystemDocument, Stat, StatDocument

connection = Connection(credentials['host'], credentials['port'])
db = getattr(connection, credentials['database'])
pool = ConnectionPool(host=redis_server['host'],port=redis_server['port'],db=0)
redis_connection = Redis(connection_pool = pool)

q_medium = Queue('medium', connection=redis_connection)
q_high = Queue('high', connection=redis_connection)

scheduler = Scheduler('default', connection = redis_connection)

def syncSystem(scheme, system):
    sys = pybikes.getBikeShareSystem(scheme, system)
    sysDoc = SystemDocument(db, connection, scheme, sys)
    sysDoc.save()
    syncStations(sys, True)

def syncStation(station_chunk, tag, resync = False, reschedule = False):
    print "Processing chunk"
    for station in station_chunk:
        station.update()
        sDoc = StationDocument(db, connection, station, tag)
        if resync or sDoc.find({'_id': station.get_hash()}).count() == 0:
            # Save this unsynched station
            print "Saving STATION %s.%s" % (tag, station.get_hash())
            sDoc.save()

        # Update the stat...
        print "Adding STAT for %s.%s" % (tag, station.get_hash())
        stat = Stat(station)
        statDoc = StatDocument(db, connection, stat)
        statDoc.save()

    if reschedule:
        scheduler.enqueue_in(timedelta(minutes=4), syncStation, station_chunk, tag, saveStat, reschedule)

def syncStations(system, resync = False, reschedule = False):
    system.update()
    #Async stations in parallel...
    print "Generating chunks..."
    chunks = [system.stations[i:i+10] for i in range(0, len(system.stations), 10)]
    print "%d chunks!" % len(chunks)
    for station_chunk in chunks:
        if system.sync:
            syncStation(station_chunk, system.tag, resync)
        else:
            q_high.enqueue(syncStation, station_chunk, system.tag, resync, reschedule)

    if system.sync and reschedule:
        scheduler.enqueue_in(timedelta(minutes=4), syncStations, system, saveStat, reschedule)

def updateSystem(scheme, system):
    instance = pybikes.getBikeShareSystem(scheme, system)
    q_medium.enqueue_call(func = syncStations,
                    args = (instance, False, False,),
                    timeout = 240)
