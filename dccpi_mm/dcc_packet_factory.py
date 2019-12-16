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
        # Preamble         Address       Data           Checksum
        # 1111111111 | 0 | 11111111 | 0 | 00000000 | 0 | 11111111 1
        self.logger.debug("Creating DCC Idle Packet")
        return(DCCGeneralPacket(address_byte=self.idleAddressByte,
                                data_bytes=['0b00000000']))

    def DCCResetPacket(self):
        # Idlepacket
        # Preamb le        Address       Data           Checksum
        # 1111111111 | 0 | 11111111 | 0 | 00000000 | 0 | 11111111 1
        self.logger.debug("Creating DCC Reset Packet")
        return(DCCGeneralPacket(address_byte=self.broadcastAddressByte,
                                data_bytes=['0b00000000']))

    def DCCEStopPacket(self):
        self.logger.debug("Creating DCC Emergency Packet")
        return self.DCCSpeedDirectionPacket(locoAddress=0, speedDirection={"speed": 0, "direction": "forward"})

    def DCCEStopPacket(self):
        self.logger.debug("Creating DCC Emergency Stop Packet")
        return self.DCCSpeedDirectionPacket(locoAddress=0, speedDirection={"speed": 1, "direction": "forward"})

    def DCCVerifyBitFromCVPacket(self,  bitData, bitPosition, CV, bitOperation="read"):
        self.logger.debug("Creating DCC Verify  Packet")
        # https://www.nmra.org/sites/default/files/s-9.2.1_2012_07.pdf
        # https://www.nmra.org/sites/default/files/s-9.2.3_2012_07.pdf
        #
        # Итого формат пакет без преамбулы и контроля ошибок:
        #
        # 0111CCVV 0 VVVVVVVV 0 DDDDDDDD
        #
        # 0111   - префикс который не меняется
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

        self.logger.debug("CV = {CV}, bitPosition = {bitPosition:03b}, bitOperation={bitOperation:01b}, bitData={bitData:01b}".format(CV=CV,
                                                                                                                                      bitPosition=bitPosition,
                                                                                                                                      bitOperation=bitOperation,
                                                                                                                                      bitData=bitData))
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
        packet_bytes.append("0b011110{CV_2bits:02b}".format(CV_2bits=CV_2bits))
        packet_bytes.append("0b{CV_8bits:08b}".format(CV_8bits=CV_8bits))
        packet_bytes.append("0b111{bitOperation:01b}{bitData:01b}{bitPosition:03b}".format(bitOperation=bitOperation,
                                                                                           bitData=bitData,
                                                                                           bitPosition=bitPosition))
        self.logger.debug(packet_bytes)

        # address is ignored
        return(DCCGeneralPacket(address_byte=self.broadcastAddressByte,
                                data_bytes=packet_bytes,
                                packet_type="service"))

    def DCCFunctionPacket(self, locoAddress, functionsState=None):
        """
        Build Function Control Packet
        """
        if functionsState is None:
            functionsState = {"Fn1": 0, "Fn2": 0, "Fn3": 0, "Fn4": 0, "FL": 0}
        else:
            functionsState = functionsState._asdict()
            for k in functionsState:
                # Convert bool to int if any
                functionsState[k] = int(functionsState[k])

        # Limited functions: only FN1-FN4
        # To be added!
        self.logger.debug("Creating DCC Set Function Packet")
        self.logger.debug("FunctionPacket: functionsState={functionsState}".format(functionsState=functionsState))
        allowedFunctions = ["Fn1", "Fn2", "Fn3", "Fn4", "FL"]
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
            if function not in functionsState:
                functionsState.update({function: 0})

        self.logger.debug("FunctionPacket: functionsState={functionsState}".format(functionsState=functionsState))

        functionPayload = "{FL}{Fn4}{Fn3}{Fn2}{Fn1}".format(FL=functionsState['FL'],
                                                            Fn1=functionsState['Fn1'],
                                                            Fn2=functionsState['Fn2'],
                                                            Fn3=functionsState['Fn3'],
                                                            Fn4=functionsState['Fn4'],
                                                            )
        self.logger.debug("FunctionPacket: {payload}".format(payload=functionPayload))
        commandByte = "0b{prefix}{payload}".format(prefix=self.functionGroupOnePrefix, payload=functionPayload)
        self.logger.debug(commandByte)

        return(DCCGeneralPacket(address_byte="0b{locoAddress:08b}".format(locoAddress=locoAddress),
                                data_bytes=[commandByte],
                                packet_type="control"))

    def DCCSpeedDirectionPacket(self, locoAddress, speedDirection=None):
        """
        Class builds packets for movement commnds
        """
        self.logger.debug("Creating DCC SpeedDirection Packet")
        self.logger.debug("SpeedDirectionPacket: speedDirection={speedDirection}".format(speedDirection=speedDirection))

        # Defaults for speed/direction
        if not speedDirection:
            speedDirection = {"speed": 0, "direction": "forward"}

        # Refactoring: using namedtuple instead of dicts.
        # Now I had to support both "old" dicts and "new"
        # namedtuples.
        if not isinstance(speedDirection, dict):
            speedDirection = speedDirection._asdict()

        # Possible directions are "forward" and "reverse"
        # https://www.nmra.org/sites/default/files/s-9.2.1_2012_07.pdf
        # These two instructions have these formats:
        # * for Reverse Operation 010DDDDD
        # * for Forward Operation 011DDDDD
        if speedDirection["direction"] == "forward":
            speedPrefix = "011"
        else:
            speedPrefix = "010"
        self.logger.debug("SpeedDirectionPacket: speedPrefix={speedPrefix}".format(speedPrefix=speedPrefix))
        # A speed and direction instruction is used send information to motors connected
        # to Multi Function Digital Decoders.
        # Instruction "010" indicates a Speed and Direction Instruction for reverse operation and
        # instruction "011" indicates a Speed and Direction Instruction for forward operation.
        # In these instructions the data is used to control speed with bits 0-3 being defined exactly
        # as in S-9.2 Section B.
        #
        # If Bit 1 of CV#29 has a value of one (1), then bit 4 is used as
        # an intermediate speed step, as defined in S-9.2, Section B.
        # If Bit 1 of CV#29 has a value of zero (0), then bit 4 shall be used to control FL3.
        # In this mode
        # Speed U0000 is stop
        # speed U0001 is emergency stop
        # speed U0010 is the first speed step
        # speed U1111 is full speed.
        #
        # This provides 14 discrete speed steps in each direction.
        #
        # If a decoder receives a new speed step that is within one step of current speed step,
        # the Digital Decoder may select a step half way between these two speed steps.
        # This provides the potential to control 56 speed steps should the command station
        # alternate speed packets.
        #
        # Decoders may ignore the direction information transmitted in a broadcast packet
        # for Speed and Direction commands that do not contain stop or emergency stop information.

        speedData = "0{speed:04b}".format(speed=speedDirection["speed"])
        speedByte = "0b{speedPrefix}{speedData}".format(speedPrefix=speedPrefix, speedData=speedData)

        return(DCCGeneralPacket(address_byte="0b{locoAddress:08b}".format(locoAddress=locoAddress),
                                data_bytes=[speedByte],
                                packet_type="control"))

    def DCCDecoderControlPacket(self, locoAddress, action):
        self.logger.debug("Creating DCC DecoderControlPacket Packet")
        # The decoder control instructions are intended to
        # set up or modify decoder configurations.
        # This instruction (0000CCCF) allows specific decoder features
        # to be set or cleared as defined by the value of D ("1" indicates set).
        # When the decoder has decoder acknowledgment enabled,
        # receipt of a decoder control instruction shall be acknowledged with an
        # operations mode acknowledgment.
        #
        # This instruction has the format of
        # {instruction byte} = 0000CCCF,
        # or
        # {instruction byte} = 0000CCCF DDDDDDDD

        # CCC = 000  D = "0": Digital Decoder Reset - A Digital Decoder Reset shall erase all volatile memory
        #            (including and speed and direction data), and return to its initial power up
        #            state as defined in S- 9.2.4 section A. Command Stations shall not send packets too
        #            addresses 112-127
        #            for 10 packet times following a Digital Decoder Reset. This is to ensure that the decoder does not
        #            start executing service mode instruction packets as operations mode packetso
        #            (Service Mode instruction packets have a short address in the range of 112 to 127 decimal.)
        #
        #            D = "1": Hard Reset - Configuration Variables 29, 31 and 32 are reset to its factory default
        #            conditions, CV#19 is set to "00000000" and a Digital Decoder reset (as in the above instruction)
        #            shall be performed.
        #
        # CCC = 001  Factory Test Instruction - This instruction is used by manufacturers to test
        #            decoders at the factory.
        #            It must not be sent by any command station during normal operation.
        #            This instruction may be a multi-byte instruction.
        # CCC = 010  Reserved for future use

        # CCC = 011 Set Decoder Flags (see below) https://www.nmra.org/sites/default/files/s-9.2.1_2012_07.pdf
        # CCC = 100 Reserved for future use
        # CCC = 101 Set Advanced Addressing (CV#29 bit 5)
        # CCC = 110 Reserved for future use
        # CCC = 111 D= "1": Decoder Acknowledgment Request

        # TODO!
        # actions =  {
        #    "reset"                : "0000",
        #    "hardReset"            : "0001",
        #    "setFlags"             : "011",
        #    "setAdvancedAddressing": "101",
        #    "acknowledgmentRequest": "1111"
        # }

        actions = {
            "acknowledgmentRequest": "1111"
        }

        if actions in actions:
            decoderControlPacketByte = "0b0000{actionData}".format(actionData=actions[action])
            return(DCCGeneralPacket(address_byte="0b{locoAddress:08b}".format(locoAddress=locoAddress),
                                    data_bytes=[decoderControlPacketByte]))
        else:
            self.logger.debug("Uncknown or not implemented action, sending Idle packet")
            return(DCCGeneralPacket(address_byte=self.idleAddressByte,
                                    data_bytes=['0b00000000']))

    def DCCConsistControlPacket(self):
        # Not implemented
        return(DCCGeneralPacket(address_byte=self.idleAddressByte,
                                data_bytes=['0b00000000']))
