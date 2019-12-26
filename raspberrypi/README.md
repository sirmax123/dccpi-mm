# dccpi-mm
My own version of DCC for Raspberry
# dccpi-mm is my own implementation of Digital Control for trains models

```
import dccpi_mm as dccpi
a = dccpi.DCCEncoder()
print(a)
a.setup()
a.send_bit_string('110011001010', 10000)
```

#More complex examples
Please see examples folder
* base_station.py - runs  DCC Control station
* loco_control.py - simple CLI loco control
