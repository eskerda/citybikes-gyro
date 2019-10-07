import sys
from os import environ

# Propagate any KEY_<SYSTEM> env variables
for key in environ.keys():
    if key.startswith('KEY_'):
        attr = key[4:].lower()
        setattr(sys.modules[__name__], attr, environ[key])