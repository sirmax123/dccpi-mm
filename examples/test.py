import sys
import dccpi_mm as dccpi
from bitstring import BitArray
#from queue import Queue
from multiprocessing import Queue
import time


#time.sleep(60)
a = dccpi.DCCHardware()
#print a
a.setup()
#a.send_bit_string('110011001010', 1000)

loco_addr = BitArray('0b00001001')
preamble  = BitArray('0b1111111111111111')
### Working
#preamble  = BitArray('0b1111111111')
#commandBack    = BitArray('0b01001111')
#commandForward = BitArray('0b01101111')



commandBack    = BitArray('0b01000011')
commandForward = BitArray('0b01100011')



commandFn = BitArray('0b10010001') # Head light
#commandFn = BitArray('0b10010010')
#commandFn = BitArray('0b10000100')
#commandFn = BitArray('0b10001000')



pf = dccpi.DCCPacketFactory()
idlePacket = pf.DCCIdlePacket().to_bit_string()
setFunctionPacket = pf.FunctionPacket(locoAddress = 9, functionsState = {"FL": 1, "Fn1": 1}).to_bit_string()
#setFunctionPacket = pf.FunctionPacket(locoAddress = 5, functionsState = {"Fn3": 1}).to_bit_string()

speedDirectionPacket = pf.SpeedDirectionPacket(locoAddress = 9, speedDirection = {"speed": 12, "direction": "reverse"}).to_bit_string()

#print(idlePacket)

command=commandFn
checksumm = loco_addr ^ command
pkt="{preamble:}0{loco_addr}0{commnad}0{checksumm}1".format(preamble=preamble.bin, loco_addr=loco_addr.bin, commnad=command.bin, checksumm=checksumm.bin)
print(setFunctionPacket)
print(pkt)

#1111111111111111 0000010010100000010100010001
#1111111111111111 0000010010100100010100110001

#command=BitArray('0b10011111') # Head Light
#command=BitArray('0b10111111') #
a.send_bit_string(idlePacket, 100)
a.send_bit_string(setFunctionPacket, 3)
a.send_bit_string(idlePacket, 10)
a.send_bit_string(speedDirectionPacket, 3)
#a.send_bit_string(pkt, 3)
a.send_bit_string(idlePacket, 1000)

a.powerdown()
sys.exit()




command=commandForward
checksumm = loco_addr ^ command

pkt="{preamble:}0{loco_addr}0{commnad}0{checksumm}1".format(preamble=preamble.bin, loco_addr=loco_addr.bin, commnad=command.bin, checksumm=checksumm.bin)


command=commandFn
checksumm = loco_addr ^ command

a.send_bit_string(idlePacket, 100)
a.send_bit_string(pkt, 10)

pkt="{preamble:}0{loco_addr}0{commnad}0{checksumm}1".format(preamble=preamble.bin, loco_addr=loco_addr.bin, commnad=command.bin, checksumm=checksumm.bin)

#print(pkt)
#1111111111 0 00001001 0 01001000 0 01000001 1
#1111111111|0|00000011|0|01001000|0|01001011|1
#a.send_bit_string('11111111100000100100100100000b10000011', 100)
#print(idlePacket)

a.send_bit_string(idlePacket, 100)
a.send_bit_string(pkt, 10)
a.send_bit_string(idlePacket, 800)
sys.exit()
time.sleep(1)
command=commandBack
checksumm = loco_addr ^ command

pkt="{preamble:}0{loco_addr}0{commnad}0{checksumm}1".format(preamble=preamble.bin, loco_addr=loco_addr.bin, commnad=command.bin, checksumm=checksumm.bin)
a.send_bit_string(pkt, 10)
a.send_bit_string(idlePacket, 800)

sys.exit()

#a.send_bit_string(pkt, 10)
#p = dccpi.DCCGeneralPacket(BitArray('0b00000011'),[ BitArray('0b11111111') ])
#print(p.to_bit_string())

#p_service = dccpi.DCCGeneralPacket(BitArray('0b00000011'),[ BitArray('0b11111111') ], 'service')
#print(p_service.to_bit_string())

pf = dccpi.DCCPacketFactory()
#idlePacket = pf.DCCIdlePacket().to_bit_string()
#print(idlePacket)

CV=1
for CV  in range(8):
    CV_1 = CV +1 
    for bitPosition in range(8):
        validate_packet = pf.DCCVerifyBitFromCVPacket(CV=CV_1, bitOperation="read", 
                                                  bitPosition=bitPosition, bitData=1).to_bit_string()
        print(validate_packet)
        a.send_bit_string(validate_packet, 3)
    #time.sleep(1)
#1111111111111111|0|00000011|0|11111111|0|11111100|1
#1111111111111111|0|00000011|0|01001000|0|01001011|1

a.debug()

a.powerdown()



#dcc_queue = Queue()
#control_station = dccpi.DCCControlStation(dcc_queue)
#control_station.start()

#111111111
#|0
#|00000011 addr
#|0
#|11101100
#|0
#|00000000
#|0
#|00000101
#|0
#|11101010|1