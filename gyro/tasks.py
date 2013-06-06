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

def syncStation(station, tag, saveStat = False, reschedule = False):
    try:
        station.update()
        if saveStat:
            stat = Stat(station)
            statDoc = StatDocument(db, connection, stat)
            statDoc.save()
        else:
            sDoc = StationDocument(db, connection, station, tag)
            sDoc.save()
        if reschedule:
            scheduler.enqueue_in(timedelta(minutes=4), syncStation, station, tag, saveStat, reschedule)
        return True
    except Exception:
        return False

def syncStations(system, saveStat = False, reschedule = False):
    system.update()
    #Async stations in parallel...
    for station in system.stations:
        if system.sync:
            syncStation(station, system.tag, saveStat)
        else:
            q_high.enqueue_call(func = syncStation,
                                args = (station, system.tag, saveStat, reschedule,),
                                timeout = 240)
    if system.sync and reschedule:
        scheduler.enqueue_in(timedelta(minutes=4), syncStations, system, saveStat, reschedule)

def updateSystem(scheme, system):
    instance = pybikes.getBikeShareSystem(scheme, system)
    syncStations(instance, True, False)
