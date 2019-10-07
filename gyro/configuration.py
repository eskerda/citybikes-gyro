from os import environ

db_credentials = {
    'host': environ.get('MONGODB_HOST', 'localhost'),
    'port': int(environ.get('MONGODB_PORT', 27017)),
    'database': environ.get('MONGODB_DATABASE', 'citybikes')
}

redis_server = {
    'db': int(environ.get('REDIS_DB', 0)),
    'host': environ.get('REDIS_HOST', 'localhost'),
    'port': int(environ.get('REDIS_PORT', 6379))
}

proxify = []

ignore = []
