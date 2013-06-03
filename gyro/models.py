# -*- coding: utf-8 -*-
# Copyright (C) 2010-2012, eskerda <eskerda@gmail.com>
# Distributed under the AGPL license, see LICENSE.txt

class Document(object):
    
    __collection__ = None
    data = {}

    def __init__(self, db, connection, *args, **kwargs):
        self.collection = getattr(db, self.__collection__)
        self.connection = connection
        self.db = db
        if len(args) > 0:
            self.__load__(*args, **kwargs)

    def __getattr__(self, attr):
        if attr in self.data:
            return self.data[attr]
        else:
            err = '\'%s\' object has no attribute \'%s\'' % (self.__class__.__name__, attr)
            raise AttributeError(err)

    def __load__(self, *args, **kwargs):
        pass

    def save(self, safe=True, *args, **kwargs):
        return self.collection.save(self.data, safe, *args, **kwargs)

    def read(self, id):
        self.data = self.collection.find_one({'_id': id})

class Stat(object):
    def __init__(self, station):
        self.station_id = station.get_hash()
        self.bikes = station.bikes
        self.free = station.free
        self.timestamp = station.timestamp
        self.extra = station.extra

class StatDocument(Document):
    __collection__ = 'station_stats'

    def __load__(self, stat):

        self.data = {
            'station_id': stat.station_id,
            'bikes': stat.bikes,
            'free': stat.free,
            'timestamp': stat.timestamp,
            'extra': stat.extra
        }
    def save(self, safe = True, *args, **kwargs):
        # Get last stat from this station document
        stationDoc = StationDocument(self.db, self.connection)
        stationDoc.read(self.station_id)
	if 'last_stat' in stationDoc.data:
            last_stat = stationDoc.data['last_stat']
        else:
	    last_stat = None
        # Create a new stat entry if it differs from the last one
        if last_stat is None or \
	   last_stat['bikes'] != self.data['bikes'] or \
           last_stat['free'] != self.data['free']:
                super( StatDocument, self).save(safe, *args, **kwargs)
        # Update last_stat on station relation.
        stationDoc.data['last_stat'] = self.data
        stationDoc.save()



class StationDocument(Document):
    __collection__ = 'stations'

    def __load__(self, station, network_id, _id = None):

        self.data = {
            '_id': station.get_hash(),
            'latitude': station.latitude,
            'longitude': station.longitude,
            'name': station.name,
            'network_id': network_id,
            'extra': station.extra
        }
        if _id is not None:
            self.data['_id'] = _id

class SystemDocument(Document):
    __collection__ = 'systems'

    def __load__(self, schema, system):
        self.data = {
            '_id': system.tag,
            'schema': schema 
        }
        self.data = dict(self.data, ** system.meta)

