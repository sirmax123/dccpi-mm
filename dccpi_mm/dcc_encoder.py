import sys
#from .dcc_packet_factory import DCCPacketFactory

import dcc_rpi_encoder_c

class DCCEncoder(object):
    """
    A DCC encoder takes a packet or packets and encodes them into the
    DCC protocol electrical standard.

    This class is meant to be extended by subclasses that implement
    the relevant methods to actually send the bits (a dummy output would only
    print it in screen, a RPI class would use GPIO to send them)
    """
    MICROSECOND_DIV = 1000000.0

    def __init__(self,
                 bit_one_part_min_duration=55,  # microseconds
                 bit_one_part_max_duration=61,
                 bit_one_part_duration=58,
                 bit_zero_part_min_duration=95,
                 bit_zero_part_max_duration=9900,
                 bit_zero_part_duration=100,
                 packet_separation=0):
        self.bit_one_part_min_duration = bit_one_part_min_duration
        self.bit_one_part_max_duration = bit_one_part_max_duration
        self.bit_one_part_duration = bit_one_part_duration
        self.bit_zero_part_min_duration = bit_zero_part_min_duration
        self.bit_zero_part_max_duration = bit_zero_part_max_duration
        self.bit_zero_part_duration = bit_zero_part_duration
        self.packet_separation = packet_separation

        self._payload = []
#        self.idle_packet = DCCPacketFactory.idle_packet()
#        self.reset_packet = DCCPacketFactory.reset_packet()
#        self.stop_packet = DCCPacketFactory.stop_packet()
#        dcc_rpi_encoder_c.dcc_rpi_encoder_c_setup()

    def send_bit_string(self, bit_string, times):
        """
        We outsource this to our C extension which can
        reliably send the bits with the correct timing.

        Passing random length arguments to C extension functions is a pain
        except for strings. So we just pass in packets as strings...
        """
        return dcc_rpi_encoder_c.send_bit_array(bit_string,
                                                times,
                                                self.bit_one_part_duration,
                                                self.bit_zero_part_duration,
                                                self.packet_separation)


    def setup(self):
        return dcc_rpi_encoder_c.setup()
