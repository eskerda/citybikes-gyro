from pymongo import Connection

c = Connection()
db = c.citybikes

systems = db.systems.find()

for system in systems:
    stations = db.stations.find({'network_id':system['_id']})
    print "Name: %s".encode('utf-8') % system['name']
    print "# Stations: %d".encode('utf-8') % stations.count()
    print "--- Stuff ---".encode('utf-8')
    for station in stations:
        print "> %s" % station['name'].encode('utf-8')
        print "Bikes: %d" % station['last_stat']['bikes']
        print "Free: %d" % station['last_stat']['free']
	print "Timestamp: %s" % station['last_stat']['timestamp']
        print "--------^".encode('utf-8')
    print "------------------------".encode('utf-8')
