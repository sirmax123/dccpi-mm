#!/usr/bin/env python3


# Simple controlstation example

import dccpi_mm as dccpi

COMMANDS_QUEUE = "dcc_command"
EMERGENCY_QUEUE = "dcc_emergency"
REDIS_ARGS = {
    'host': 'localhost',
    'port': 6379,
    'db': 0
}


# Create redisq queue reader (in furure may be replaced with ZeroMQ queue or any other
# queue implementation.
commands_queue_reader = dccpi.RedisQueueReader(COMMANDS_QUEUE, EMERGENCY_QUEUE, **REDIS_ARGS)

control_station = dccpi.DCCControlStation(commands_queue_reader, idle_packets_count=20)
control_station.main_loop()
