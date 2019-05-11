import sys
import threading
import os
import Queue
import time
#from .dcc_packet_factory import DCCPacketFactory

#import dcc_rpi_encoder_c
from .dcc_logger         import getLogger
from .dcc_packet_factory import DCCPacketFactory
from .dcc_hardware       import DCCHardware



class DCCControlStation(threading.Thread):
    def __init__(self,queue):

        threading.Thread.__init__(self)
        self.queue = queue

        self.logger = getLogger('DCCControlStation')
        self.logger.debug('DCCControlStation init')

        self.packet_factory  = DCCPacketFactory()
        self.idle_packet = self.packet_factory.DCCIdlePacket().to_bit_string()

        self.station_hardware = DCCHardware()
        print(self.idle_packet)


    def run(self):
        # Endless loop
        self.logger.debug("Starting loop")
        while True:
            if not self.queue.empty():
               self.dccPacket = self.queue.get()
               self.logger.debug("Got DCC Packet from queue: {packet}".format(packet=self.packet))
            else:
                self.logger.debug("Empty queue, sending IDLE DCC Packet")
                self.station_hardware.send_bit_string(self.idle_packet, 1)
                time.sleep(1)