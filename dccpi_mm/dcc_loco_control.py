import redis
import time
import json

from .dcc_logger import getLogger
from .dcc_packet_factory import DCCPacketFactory
from .dcc_hardware import DCCHardware
from .dcc_redis_queue import RedisQueue


class DCCKeyboardLocoControl(object):
    """
    Class id defined to be used in console application
    and and handle keys
    By default arrow keys up/down areused for speed control,
    and numbers are used to control functions
    """
    def __init__(self, loco_address, commands_queue_name,
                 emergency_queue_name, **redis_kwargs):

        self.lolco_address = loco_address
        self.commands_queue = RedisQueue(commands_queue_name, **redis_kwargs)
        self.emergency_queue = RedisQueue(emergency_queue_name, **redis_kwargs)
        self.loco_functions = {
            'FL':  0,
            "Fn1": 0,
            "Fn2": 0,
            "Fn3": 0,
            "Fn4": 0,
        }
        self.loco_speed = 0
        self.loco_address = loco_address
        self.loco_direction = None
        # Prededefined keys
        self.UP_SPEED_KEYS = ('up')
        self.DECREASE_SPEED_KEYS = ('down')
        self.INCREASE_SPEED_KEYS = ('up')
        self.DECREASE_SPEED_KEYS = ('down')
        # Lists of keys to activate/deactivate functions
        self.FUNCTION_KEY_MAPPING = {
            'FL': ('0'),
            '1':  ('1'),
            '2':  ('2'),
            '3':  ('3'),
            '4':  ('4')
        }
        # used to avoid hardcoding class name
        self.logger = getLogger(type(self).__name__)
        self.logger.debug('Init')

    def exit(self):
        """
        Base control station send eStop packet on track if any data in
        emergency queue
        so any payload can be used for emergency packet
        """
        self.emergency_queue.put('{ "action": "emergency_stop" }')

    def key_handler(self, key):
        """
        Simple key handler
        """
        self.logger.debug(key)
        if key in self.INCREASE_SPEED_KEYS:
            # Set direction if not defined.
            # Direction can be changed only if speed = 0
            if (self.loco_speed == 0) and (self.loco_direction != 'forward'):
                self.loco_direction = 'forward'
            else:
                # Max speed is 14
                self.loco_speed = min(self.loco_speed + 1, 14)

        if key in self.DECREASE_SPEED_KEYS:
            # Set direction if not defined
            if (self.loco_speed == 0) and (self.loco_direction != 'reverse'):
                self.loco_direction = 'reverse'
            else:
                # Min speed is 0
                self.loco_speed = max(self.loco_speed - 1, -14)

        if (key in self.DECREASE_SPEED_KEYS) or (key in self.INCREASE_SPEED_KEYS):
            command = {
                'action':       'move',
                'loco_address': self.loco_address,
                'direction':    self.loco_direction,
                'speed':        abs(self.loco_speed)
            }
            self.commands_queue.put(json.dumps(command))
            return command

        # Key is not in speed change keys, need to check functions key
        for function_name, function_keys in self.FUNCTION_KEY_MAPPING.items():
            if key in function_keys:
                # Invert function state if function key is pressed.
                self.loco_functions[function_name] = not self.loco_functions[function_name]

            command = {
                'action':          'functon',
                'loco_address':    self.loco_address,
                'functions_state': self.loco_functions
            }

        self.commands_queue.put(json.dumps(command))

        return command
