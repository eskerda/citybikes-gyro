from pymongo import Connection

c = Connection()
c.drop_database('citybikes')
