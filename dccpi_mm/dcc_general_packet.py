import sys
from bitstring import BitArray
from dcc_logger import getLogger


# packet example 111111111|0|00000011|0|01001000|0|01001011|1
# preamble:    111111111 (14 or more)
# byte startbit  0
# address byte   00000011
# separator bit  0
# data           01001000
# separtator bit 0
# checksumm      01001011
# Finish bit     1



class DCCGeneralPacket(object):
    """
    A class to build any DCC packet given an address and data bytes
    """
    def __init__(self,
                 address_byte,
                 data_bytes=[],
                 packet_type="control"
                ):
        """
        All arguments simle binary/hex strings: 0xFF 0b2121
        """
        self.logger = getLogger("DCCGeneralPacket")
        self.logger.debug("DCCGeneralPacket init")
        self.logger.debug("{data_bytes}".format(data_bytes=data_bytes))
        if packet_type == 'service':
        # Servic e preamble is 25 bits
            self.preamble = BitArray('0b1111111111111111111111111')
            #self.preamble = BitArray('0b1111111111111111')
            # there are no address byte in service mode packets
            self.address_byte = BitArray(data_bytes.pop(0))
        else:
        # A command station must send a minimum of 14 preamble bits
            self.preamble = BitArray('0b1111111111111111')
            self.address_byte = BitArray(address_byte)

        self.logger.debug("Preamble is set: {p}".format(p=self.preamble))
        self.packet_start_bit = BitArray('0b0')
        self.data_byte_start_bit = BitArray('0b0')
        self.data_bytes = map(BitArray, data_bytes)
        self.logger.debug("data is: {data}".format(data=self.data_bytes))

        if sys.version_info.major >= 3:
            self.data_bytes = list(self.data_bytes)

        self.packet_end_bit = BitArray('0b1')
        self.logger.debug("Address Byte: {address}".format(address=self.address_byte))

        assert(len(self.address_byte) == 8)
        for byte in self.data_bytes:
            self.logger.debug("Data byte: {byte}".format(byte=byte))
            assert(len(byte) == 8)

    @staticmethod
    def from_bit_array(int_array):
        """
        Given [1, 1,...] array try to decode a packet
        """
        packet = BitArray(int_array)
        # preamble = packet[0:12]
        address_byte = packet[13:21]
        data_bytes = packet[22:-1]
        dbit = 0
        data_bytes_a = []
        while dbit < len(data_bytes):
            data_bytes_a.append(data_bytes[dbit:dbit+8])
            dbit += 9  # skip start bit from next data byte
        return DCCGeneralPacket(address_byte, data_bytes_a)

    def to_bit_array(self):
        """
        Builds a single string that should end up
        being serialized.

        Returns an array of True/False
        """
        packet = BitArray()
        self.logger.debug("Packet: Adding preamble")
        packet.append(self.preamble)
        self.logger.debug("Packet: [ {packet} ] {l}".format(packet=packet.bin, l=len(packet.bin)))
        debug_packet = "<-{placeholder}->".format(placeholder=('-'*len(self.preamble))[:-4])
        self.logger.debug("Packet: [ {debug_packet} ]".format(debug_packet=debug_packet))
        self.logger.debug("Packet: Adding packet start bit")
        packet.append(self.packet_start_bit)
        debug_packet = "{debug_packet}|".format(debug_packet=debug_packet)
        self.logger.debug("Packet: [ {packet} ]".format(packet=packet.bin))
        self.logger.debug("Packet: [ {debug_packet} ]".format(debug_packet=debug_packet))

        self.logger.debug("Packet: Adding address byte")
        packet.append(self.address_byte)
        debug_packet = "{debug_packet}<-Addr->".format(debug_packet=debug_packet)
        self.logger.debug("Packet: [ {packet} ]".format(packet=packet.bin))
        self.logger.debug("Packet: [ {debug_packet} ]".format(debug_packet=debug_packet))
        checksumm = self.address_byte

        for byte in self.data_bytes:
            self.logger.debug("Packet: Adding byte start bit")
            packet.append(self.data_byte_start_bit)
            debug_packet = "{debug_packet}|".format(debug_packet=debug_packet)
            self.logger.debug("Packet: [ {packet} ]".format(packet=packet.bin))
            self.logger.debug("Packet: [ {debug_packet} ]".format(debug_packet=debug_packet))
            self.logger.debug("Packet: Adding data byte [{byte}]".format(byte=byte))
            packet.append(byte)
            debug_packet = "{debug_packet}<-Data->".format(debug_packet=debug_packet)
            self.logger.debug("Packet: [ {packet} ]".format(packet=packet.bin))
            self.logger.debug("Packet: [ {debug_packet} ]".format(debug_packet=debug_packet))
            checksumm = checksumm ^ byte
        self.logger.debug("Packet: Adding byte start bit")
        packet.append(self.data_byte_start_bit)
        debug_packet = "{debug_packet}|".format(debug_packet=debug_packet)
        self.logger.debug("Packet: [ {packet} ]".format(packet=packet.bin))
        self.logger.debug("Packet: [ {debug_packet} ]".format(debug_packet=debug_packet))

        self.logger.debug("Packet: Adding checksumm")
        packet.append(checksumm)
        debug_packet = "{debug_packet}<-Summ->".format(debug_packet=debug_packet)

        self.logger.debug("Packet: [ {packet} ]".format(packet=packet.bin))
        self.logger.debug("Packet: [ {debug_packet} ]".format(debug_packet=debug_packet))

        self.logger.debug("Packet: Adding packet end bit")
        packet.append(self.packet_end_bit)
        debug_packet = "{debug_packet}|".format(debug_packet=debug_packet)
        self.logger.debug("Packet: [ {packet} ]".format(packet=packet.bin))
        self.logger.debug("Packet: [ {debug_packet} ]".format(debug_packet=debug_packet))
        return map(int, packet)

    def to_bit_string(self):
        return "".join(map(str, self.to_bit_array()))

    def __str__(self):
        """
        Allow some debuging
        """
        return "Device #%d: %s" % (self.address_byte.uint,
                                   " ".join(map(str, self.data_bytes)))
