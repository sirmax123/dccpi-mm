import json
import os
import redis
import sys
import time

#import dcc_rpi_encoder_c
from .dcc_logger         import getLogger
from .dcc_packet_factory import DCCPacketFactory
from .dcc_hardware       import DCCHardware
from .dcc_redis_queue    import RedisQueue


class DCCControlStation(object):
    """
    DCCControlStation class reads commands from queue and sends on track.
    This basic implementation does not support tornout control, track-busy-sensors etc,
    """
    def __init__(self, commands_queue, emergency_queue, idle_packets_count=10, **redis_kwargs):

        self.packet_factory = DCCPacketFactory()
        self.idle_packet = self.packet_factory.DCCIdlePacket().to_bit_string()
        self.e_stop_packet = self.packet_factory.DCCEStopPacket().to_bit_string()
        self.commands_queue = RedisQueue(commands_queue, **redis_kwargs)
        self.emergency_queue = RedisQueue(emergency_queue, **redis_kwargs)

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
                self.hardware.send_bit_string(self.packet_factory.DCCSpeedDirectionPacket(
                            locoAddress = command['loco_address'],
                            speedDirection = {
                                "speed": command['speed'],
                                "direction": command['direction']}).to_bit_string(), 1)
            elif command['action'] == 'functon':
                self.hardware.send_bit_string(self.packet_factory.DCCFunctionPacket(locoAddress = command['loco_address'],
                                            functionsState = command['functions_state']).to_bit_string(), 1)

        except KeyboardInterrupt:
            sys.exit(1)
        except Exception  as Ex:
            # ignore errors
            self.logger.debug(Ex)

    def main_loop(self):
        while True:
            while  not self.emergency_queue.empty():
                emergency_command = self.emergency_queue.get()
                self.logger.info("Emergency Command = {emergency_command}".format(emergency_command=emergency_command))
                self.hardware.send_bit_string(self.e_stop_packet, 3)

            if not self.commands_queue.empty():
                command_json = self.commands_queue.get().decode('utf-8')
                self.logger.info("Command = {command_json}".format(command_json=command_json))
                self.decode_command(command_json)

            self.hardware.send_bit_string(self.idle_packet, self.idle_packets_count)
