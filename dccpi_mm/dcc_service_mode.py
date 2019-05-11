import sys
#from .dcc_packet_factory import DCCPacketFactory

import dcc_rpi_encoder_c
from dcc_logger import getLogger

class DCCServicePacketFactory(object):
    """
    TODO
    """

    def __init__(self):
        self.logger = getLogger("DCCServicePacketFactory")
        self.logger.debug("DCCServicePacketFactory init")
