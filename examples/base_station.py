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


control_station = dccpi.DCCControlStation(COMMANDS_QUEUE, EMERGENCY_QUEUE,
                                          idle_packets_count=20, **REDIS_ARGS)
control_station.main_loop()
