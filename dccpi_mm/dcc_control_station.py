import json
import os
import redis
import sys
import time

from .dcc_logger import getLogger
from .dcc_packet_factory import DCCPacketFactory
from .dcc_hardware import DCCHardware
from .dcc_redis_queue import RedisQueue

from collections import namedtuple

SpeedDirection = namedtuple('SpeedDirection', ['speed', 'direction'])
FunctionsState = namedtuple('FunctionsState', [
    "FL",
    "Fn1",
    "Fn2",
    "Fn3",
    "Fn4",
])


class DCCControlStation(object):
    """
    DCCControlStation class reads commands from queue and sends on track.
    This basic implementation does not support tornout control, track-busy-sensors etc,
    """
    def __init__(self, commands_queue_reader, idle_packets_count=10, clean_queue_before_start=True):

        self.packet_factory = DCCPacketFactory()
        self.idle_packet = self.packet_factory.DCCIdlePacket().to_bit_string()
        self.e_stop_packet = self.packet_factory.DCCEStopPacket().to_bit_string()
        self.commands_queue_reader = commands_queue_reader

        if clean_queue_before_start:
            self.commands_queue_reader.clean_queue()

        self.hardware = DCCHardware()
        self.hardware.setup()

        self.logger = getLogger(type(self).__name__)
        self.logger.debug('DCCControlStation init')
        self.idle_packets_count = idle_packets_count

    def decode_command(self, command_json):
        """
        Method reads command from queues and sends on track.
        IF emergency_queue is NOT EMPTY eStop (emergency stop) packet will be saend on track
        """
        self.logger.info("Got DCC Command from queue: {command_json}".format(command_json=command_json))

        try:
            command = json.loads(command_json)
            self.logger.info(command)

            # For 'normal operations' there are 2 types of packets:
            # 'move':     change speed and/or direction
            # 'function': change function state
            # Other commnads are interpritaded as 'idle'
            if command['action'] == 'move':
                speed_direction = SpeedDirection(
                    command['speed'],
                    command['direction']
                )
                packet = self.packet_factory.DCCSpeedDirectionPacket(locoAddress=command['loco_address'],
                                                                     speedDirection=speed_direction)

                self.hardware.send_bit_string(packet.to_bit_string(), 1)

            elif command['action'] == 'functon':
                functions_state = FunctionsState(
                    command['functions_state']['FL'],
                    command['functions_state']['Fn1'],
                    command['functions_state']['Fn2'],
                    command['functions_state']['Fn3'],
                    command['functions_state']['Fn4']
                )

                packet = self.packet_factory.DCCFunctionPacket(locoAddress=command['loco_address'],
                                                               functionsState=functions_state)
                self.hardware.send_bit_string(packet.to_bit_string(), 1)

            else:
                # If command is detected but it is not move of functiond
                # just ignore it and send idle packet(s)
                self.hardware.send_bit_string(self.idle_packet, self.idle_packets_count)

        except KeyboardInterrupt:
            sys.exit(1)

    def main_loop(self):
        # Endless loop reads commands from queue
        for command in self.commands_queue_reader:
            # eStop command
            if command == "emergency_stop":
                self.logger.info("Emergency Command = {command}".format(command=command))
                self.hardware.send_bit_string(self.e_stop_packet, 3)
            # Idle commnads: sends idle packet with no commands
            # used for power delivery
            elif command == "idle":
                self.hardware.send_bit_string(self.idle_packet, self.idle_packets_count)
            # Command itself
            else:
                self.logger.info("Command = {command}".format(command=command))
                self.decode_command(command)

