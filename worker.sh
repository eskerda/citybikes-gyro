#!/bin/sh

rqworker -H $REDIS_HOST \
    -p $REDIS_PORT \
    -d $REDIS_DB \
    $QUEUES