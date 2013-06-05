from pymongo import Connection
from gyro.configuration import db_credentials as credentials

connection = Connection(credentials['host'], credentials['port'])
connection.drop_database('citybikes')
