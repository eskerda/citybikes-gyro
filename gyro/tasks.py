from __future__ import absolute_import
from redis import Redis
from rq import Queue
from rq_scheduler import Scheduler
from datetime import timedelta
import pybikes
from gyro.configuration import db_credentials as credentials
from pymongo import Connection
from gyro.models import StationDocument, SystemDocument, Stat, StatDocument
import memcache

connection = Connection(credentials['host'], credentials['port'])
db = getattr(connection, credentials['database'])
redis_connection = Redis()
q = Queue(connection=redis_connection)
scheduler = Scheduler('default', connection = redis_connection)

def syncSystem(scheme, system):
    sys = pybikes.getBikeShareSystem(scheme, system)
    sysDoc = SystemDocument(db, connection, scheme, sys)
    sysDoc.save()
    syncStations(sys)

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
    jobs = []
    for station in system.stations:
        if system.sync:
            syncStation(station, system.tag, saveStat)
        else:
            job = q.enqueue(syncStation, station, system.tag, saveStat, reschedule)
            jobs.append(job)
    if system.sync and reschedule:
        scheduler.enqueue_in(timedelta(minutes=4), syncStations, system, saveStat, reschedule)
    """
    if system.sync is False:
        # Blocking... !
        # Wait for all these jobs to end
        res = True
        while res:
            jres = [j for j in jobs if j.result is None]
            res = len(jres) > 0
    """

def updateSystem(scheme, system):
    instance = pybikes.getBikeShareSystem(scheme, system)
    syncStations(instance, True, True)