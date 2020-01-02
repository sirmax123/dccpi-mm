# This file is executed on every boot (including wake-boot from deepsleep)
# import esp
# esp.osdebug(None)

import network
import utime
import urequests
import ubinascii
import random
import os
import copy
import json


DEFAULT_CONFIG = {
    "tornout_id": 1,
    "dhcp_name_prefix": "tornout",
    "ssid": "default_ssid",
    "password": "default_password",
    "pins": {
    }
}

CONFIG_FILE = "config.txt"


# System functions
def df():
    "Show FS (like linux tool `df`"
    s = os.statvfs('//')
    return ('{0} MB'.format((s[0]*s[3])/1048576))


def free(full=False):
    "Shows free memory, like lkinux tool `free`"
    F = gc.mem_free()
    A = gc.mem_alloc()
    T = F+A
    P = '{0:.2f}%'.format(F/T*100)
    if not full:
        return P
    else:
        return ('Total:{0} Free:{1} ({2})'.format(T, F, P))


def connect(ssid='default_ssid', password='default_pasword', connect_timeout=10, pause=1):
    """
    Connect to the existing wireless network
    """
    print("Connecting")
    deadline = utime.ticks_add(utime.ticks_ms(), connect_timeout*1000)
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('Connecting to network...')
        sta_if.active(True)
        sta_if.config(dhcp_hostname='turnout{}')
        sta_if.connect(ssid, password)
        while not sta_if.isconnected():
            if utime.ticks_diff(deadline, utime.ticks_ms()) < 0:
                print("Can't connect: timout exceeded")
                return False
            else:
                pass
        print('network config:', sta_if.ifconfig())
        return sta_if
    else:
        print('already connected')
        print('network config:', sta_if.ifconfig())
        return sta_if


def create_acces_point():
    """
    Create access point with random open network and
    setup random IP. Need for intial setup.
    """
    access_point = network.WLAN(network.AP_IF)
    octet_3 = random.randint(0, 254)
    mac = ubinascii.hexlify(access_point.config('mac'), ':').decode()
    ssid = "🚂__RailWay_IP_192_168_{o3}_1___{m}".format(o3=octet_3, m=mac)
    access_point.active(True)
    access_point.config(essid=ssid)

    # Wait for setup is finished
    while access_point.active() is False:
        pass

    access_point.ifconfig(('192.168.{o3}.1'.format(o3=octet_3),
                           '255.255.255.0', '', '8.8.8.8'))
    print(ssid)
    print('192.168.{o3}.1'.format(o3=octet_3))
    return access_point


def load_config_from_disk():
    """
    Load saved configuration from persistant storage if possible
    """
    try:
        with open(CONFIG_FILE) as config_file_handler:
            config_txt = config_file_handler.read()
            config_json = json.loads(config_txt)
            return config_json
    except Exception as Ex:
        print(Ex)
        return DEFAULT_CONFIG


def save_config_to_disk(config):
    """
    Save configuration to the persistent storage
    """
    try:
        with open(CONFIG_FILE, 'w') as config_file_handler:
            config_file_handler.write(json.dumps(config))
            return True
    except Exception:
        print(Ex)
        return False


def delete_config_from_disk():
    """
    Delete saved config from disk (reset to defaults)
    """
    try:
        os.remove(CONFIG_FILE)
        return True
    except Exception as Ex:
        return False


def basic_init():
    """
    Check config and connect to the wireless
    network or create access_point
    """
    CONFIG = load_config_from_disk()
    WIFI = connect(ssid=CONFIG["ssid"],
                   password=CONFIG['password'])
    if not WIFI:
        create_acces_point()
    return CONFIG


CONFIG = basic_init()
