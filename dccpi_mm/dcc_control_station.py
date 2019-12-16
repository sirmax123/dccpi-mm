import json
import os
import redis
import sys
import time

from .dcc_logger import getLogger
from .dcc_packet_factory import DCCPacketFactory
from .dcc_hardware import DCCHardware
from .dcc_redis_queue import RedisQueue


class DCCControlStation(object):
    """
    DCCControlStation class reads commands from queue and sends on track.
    This basic implementation does not support tornout control, track-busy-sensors etc,
    """
    def __init__(self, commands_queue, emergency_queue, idle_packets_count=10,
                 clean_queue_before_start=True, **redis_kwargs):

        self.packet_factory = DCCPacketFactory()
        self.idle_packet = self.packet_factory.DCCIdlePacket().to_bit_string()
        self.e_stop_packet = self.packet_factory.DCCEStopPacket().to_bit_string()
        self.commands_queue = QueueReader(commands_queue, emergency_queue, **redis_kwargs)

        if clean_queue_before_start:
            self.commands_queue.clean_queue()

        self.hardware = DCCHardware()
        self.hardware.setup()

        self.logger = getLogger('DCCControlStation')
        self.logger.debug('DCCControlStation init')
        self.idle_packets_count = idle_packets_count

    def decode_command(self, command_json):
        """
        Method reads command from queues and sends on track.
        IF emergency_queue is NOT EMPTY eStop (emergency stop) packet will be saend on track
        """
        self.logger.info("Got DCC Command from queue: {command_json}".format(command_json=command_json))
        command = json.loads(command_json)
        try:
            if command['action'] == 'move':
                speedDirection = {
                    "speed": command['speed'],
                    "direction": command['direction']
                }
                packet = self.packet_factory.DCCSpeedDirectionPacket(locoAddress=command['loco_address'],
                                                                     speedDirection=speedDirection)
                self.hardware.send_bit_string(packet.to_bit_string(), 1)

            elif command['action'] == 'functon':
                packet = self.packet_factory.DCCFunctionPacket(locoAddress=command['loco_address'],
                                                               functionsState=command['functions_state'])

            self.hardware.send_bit_string(packet.to_bit_string(), 1)

        except KeyboardInterrupt:
            sys.exit(1)
        except Exception as Ex:
            # ignore errors
            self.logger.debug(Ex)

    def main_loop(self):
        while True:
            for command in self.commands_queue:
                if command == "emergency_stop":
                    self.logger.info("Emergency Command = {emergency_command}".format(
                              emergency_command=emergency_command))
                    self.hardware.send_bit_string(self.e_stop_packet, 3)
                else:
                    self.logger.info("Command = {command}".format(command=command))
                    self.decode_command(command)

            self.hardware.send_bit_string(self.idle_packet, self.idle_packets_count)


class QueueReader(object):
    """
    This class is designed to return command from redis queue
    """
    def __init__(self, commands_queue, emergency_queue,  **redis_kwargs):

        self.logger = getLogger('QueueReader')
        self.commands_queue = RedisQueue(commands_queue, **redis_kwargs)
        self.emergency_queue = RedisQueue(emergency_queue, **redis_kwargs)

    def __iter__(self):
        return self

    def clean_queue(self):
        """
        No need to read old packets saved in queue before station is started.
        This method just reads everething and removes from queue.
        """
        self.logger.info("Running Cleanup")
        while not self.emergency_queue.empty():
            emergency_command = self.emergency_queue.get()
            self.logger.info("Cleaning Emergency Queue: {emergency_command}".format(command_json=command_json))

        while not self.commands_queue.empty():
            command_json = self.commands_queue.get().decode('utf-8')
            self.logger.info("Cleaning Commands Queue: {command_json}".format(command_json=command_json))

    def __next__(self):
        if not self.emergency_queue.empty():
            emergency_command = self.emergency_queue.get()
            self.logger.info("Emergency Command = {emergency_command}".format(emergency_command=emergency_command))
            return "emergency_stop"

        elif not self.commands_queue.empty():
            command_json = self.commands_queue.get().decode('utf-8')
            self.logger.info("Command = {command_json}".format(command_json=command_json))
            return command_json
        else:
            raise StopIteration
