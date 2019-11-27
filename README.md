# dccpi-mm
My own version of DCC for Raspberry 


Minumal example:

import dccpi_mm as dccpi


a = dccpi.DCCEncoder()
print a
a.setup()
a.send_bit_string('110011001010', 10000)
