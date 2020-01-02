# Basic Implementatiuon of ESP32-based turnout controller


## Getting started with ESP32 dev board
### Install MicroPython (1.12 is latest)
Download micropython: https://micropython.org/download#esp32
```
esptool.py --chip esp32 --port /dev/ttyUSB0 erase_flash
```
```
esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 460800 write_flash -z 0x1000 /root/esp32-idf3-20191220-v1.12.bin
```
Install deployment tool:
```
pip install wonderbits-ampy
```
Test connection:
```
# wb_ampy  -p /dev/ttyUSB0 -b 115200  ls
/boot.py
```
