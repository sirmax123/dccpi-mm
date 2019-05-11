from .dcc_logger import getLogger
from .dcc_general_packet import DCCGeneralPacket
from bitstring import BitArray

class DCCPacketFactory(object):
    def __init__(self, address_byte='0b1111111'):
        self.logger = getLogger("DCCPacketFactory")
        self.logger.debug("DCCPacketFactory init")

        self.idleAddressByte = '0b11111111'
        self.broadcastAddressByte = '0b00000000'

        self.functionGroupOnePrefix = '100'

    def DCCIdlePacket(self):
        # Idlepacket
        # Preamble        Address       Data           Checksum
        #1111111111 | 0 | 11111111 | 0 | 00000000 | 0 | 11111111 1
        self.logger.debug("Creating DCC Idle Packet")
        return(DCCGeneralPacket(address_byte=self.idleAddressByte,
                                data_bytes=['0b00000000']))

    def DCCVerifyBitFromCVPacket(self,  bitData, bitPosition, CV, bitOperation="read"):
        self.logger.debug("Creating DCC Verify  Packet")
        # https://www.nmra.org/sites/default/files/s-9.2.1_2012_07.pdf
        #
        # Configuration Variable Access Instruction - Long Form
        #
        # The long form allows the direct manipulation of all CVs. 
        # This instruction is valid both when the Digital Decoder has its 
        # long address active and short address active. 
        #
        # Digital Decoders shall not act on this instruction 
        # if sent to its consist address. 
        #
        # The format of the instructions using Direct CV addressing is:
        #
        # 1110CCVV 0 VVVVVVVV 0 DDDDDDDD
        #
        # data byte being the most significant bits of the address. 
        # The Configuration variable being addressed is the provided 10-bit address plus 1.
        #
        # For example, to address CV#1 the 10 bit address is 00 00000000
        #
        # The defined values for Instruction type (CC) are:
        # CC=00 Reserved for future use
        # CC=01 Verify byte 
        # CC=11 Write byte
        # CC=10 Bit manipulation
        #
        # Type = "01" VERIFY BYTE
        # The contents of the Configuration Variable as indicated by the 10-bit 
        # address are compared with the data byte (DDDDDDDD). If the decoder successfully 
        # receives this packet and the values are identical, 
        # the Digital Decoder shall respond with the contents of the CV as the 
        # Decoder Response Transmission, if enabled.
        #


        #The actual Configuration Variable desired is selected via the 10-bit address with the 2-bit address (VV) in the first

        # Type = "11" WRITE BYTE
        # The contents of the Configuration Variable as indicated by the 10-bit address are 
        # replaced by the data byte (DDDDDDDD). 
        # Two identical packets are needed before the decoder shall modify a configuration variable. 
        # These two packets need not be back to back on the track. 
        # However any other packet to the same decoder will invalidate the write operation. (This includes broadcast packets.) 
        # If the decoder successfully receives this second identical packet, 
        # it shall respond with a configuration variable access acknowledgment.
        #
        # Type = "10" BIT MANIPULATION
        # The bit manipulation instructions use a special format for the data byte (DDDDDDDD):
        # 111CDBBB
        # Where BBB represents the bit position within the CV, D contains the value of the bit 
        # to be verified or written, and C describes whether the operation is a verify bit or a write bit operation.
        # C = "1" WRITE BIT
        # C = "0" VERIFY BIT

        # The VERIFY BIT and WRITE BIT instructions operate in a manner similar to the 
        # VERIFY BYTE and WRITE BYTE instructions (but operates on a single bit).
        # Using the same criteria as the VERIFY BYTE instruction, an operations mode acknowledgment will be generated in 
        # response to a VERIFY BIT instruction if appropriate. Using the same criteria as the WRITE BYTE instruction, 
        # a configuration variable access acknowledgment will be
        # generated in response to the second identical WRITE BIT instruction if appropriate

        # Итого формат пакет без преамбулы и контроля ошибок:
        #
        # 1110CCVV 0 VVVVVVVV 0 DDDDDDDD
        #
        # 111   - префикс который не меняется
        # CC=10 - манипуляции с отдельными битами
        # VV 0 VVVVVVVV (c разделителем) - адрес  CV, 10 бит позволяют адресовать от 0 до 1023 CV
        # DDDDDDD - данные
        #     111CDBBB
        #     111 - фиксированное значение
        #     С   - тип команды, 1 - запись 0 - чтение (верефикация)
        #     D   - Данные (1 или 0 так как операция битовая
        #     BBB - позиция бита (от 0 до 7)
        #


        if bitOperation == "write":
            bitOperation = 1
        else:
            bitOperation = 0

        self.logger.debug("CV = {CV}, bitPosition = {bitPosition:03b}, bitOperation={bitOperation:01b}, bitData={bitData:01b}".format(CV=CV, bitPosition=bitPosition, bitOperation=bitOperation, bitData=bitData))
        # CV numbers are 1, 2 ... etc, but CV addresses are 0, 1 ...
        CV = CV - 1
        # CV is 10 bit
        CV_2bits = CV >> 8
        CV_2bits_sting = "{CV_2bits:02b}".format(CV_2bits=CV_2bits)
        self.logger.debug("CV 2 bits = {CV_2bits}".format(CV_2bits=CV_2bits))
        self.logger.debug("CV 2 bits = {CV_2bits}".format(CV_2bits=CV_2bits_sting))

        # Other 8 bits of CV address
        CV_8bits = CV & 255
        CV_8bits_sting = "{CV_8bits:08b}".format(CV_8bits=CV_8bits)
        self.logger.debug("CV 8 bits = {CV_8bits}".format(CV_8bits=CV_8bits))
        self.logger.debug("CV 8 bits = {CV_8bits}".format(CV_8bits=CV_8bits_sting))

        packet_bytes = []
        packet_bytes.append("0b111010{CV_2bits:02b}".format(CV_2bits=CV_2bits))
        packet_bytes.append("0b{CV_8bits:08b}".format(CV_8bits=CV_8bits))
        packet_bytes.append("0b111{bitOperation:01b}{bitData:01b}{bitPosition:03b}".format(bitOperation=bitOperation, bitData=bitData, bitPosition=bitPosition))
        self.logger.debug(packet_bytes)
        #return(DCCGeneralPacket(address_byte=self.idleAddressByte,
        #                        data_bytes=['0b00000000'],
        #                        packet_type="service"))
        return(DCCGeneralPacket(address_byte=self.broadcastAddressByte,
                                data_bytes=packet_bytes,
                                packet_type="service"))

    def FunctionPacket(self, locoAddress, functionsState = {"Fn1": 0, "Fn2": 0, "Fn3": 0, "Fn4": 0, "FL": 0 }):
        self.logger.debug("Creating DCC Set Function Packet")
        self.logger.debug("FunctionPacket: functionsState={functionsState}".format(functionsState=functionsState))
        allowedFunctions = ["Fn1", "Fn2", "Fn3", "Fn4", "FL" ]
        # Function Group One Instruction (100)
        # The format of this instruction is 100DDDDD
        # Up to 5 auxiliary functions (functions FL and F1-F4) can be controlled
        # FL: Forward Lamp
        # by the Function Group One instruction. Bits 0-3 shall define the value of functions F1-F4
        # with function F1 being controlled by bit 0 and function F4 being controlled by bit 3.
        # A value of "1" shall indicate that the function is "on" while a value of "0"
        # shall indicate that the function is "off".
        #
        # If Bit 1 of CV#29 has a value of one (1), then bit 4 controls function FL,
        # otherwise bit 4 has no meaning

        # Set defaults to "Off" for all functions
        for function in allowedFunctions:
            if not (functionsState.has_key(function)):
                functionsState.update({function: 0})

        self.logger.debug("FunctionPacket: functionsState={functionsState}".format(functionsState=functionsState))

        functionPayload = "{FL}{Fn4}{Fn3}{Fn2}{Fn1}".format(FL=functionsState['FL'],
                                                            Fn1=functionsState['Fn1'],
                                                            Fn2=functionsState['Fn2'],
                                                            Fn3=functionsState['Fn3'],
                                                            Fn4=functionsState['Fn4'],
                                                            )
        self.logger.debug("FunctionPacket: {payload}".format(payload=functionPayload))
        commandByte = "0b{prefix}{payload}".format(prefix = self.functionGroupOnePrefix, payload=functionPayload)

        self.logger.debug(commandByte)

        return(DCCGeneralPacket(address_byte="0b{locoAddress:08b}".format(locoAddress=locoAddress),
                                data_bytes=[commandByte],
                                packet_type="control"))
