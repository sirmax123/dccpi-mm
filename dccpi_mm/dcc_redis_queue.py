import redis
from .dcc_logger import getLogger


class RedisQueue(object):
    """Simple Queue with Redis Backend"""
    def __init__(self, name, namespace='queue', **redis_kwargs):
        """The default connection parameters are: host='localhost', port=6379, db=0"""
        self.__db = redis.Redis(**redis_kwargs)
        self.key = '{namespace}:{name}'.format(namespace=namespace, name=name)

    def qsize(self):
        """Return the approximate size of the queue."""
        return self.__db.llen(self.key)

    def empty(self):
        """Return True if the queue is empty, False otherwise."""
        return self.qsize() == 0

    def put(self, item):
        """Put item into the queue."""
        self.__db.rpush(self.key, item)

    def get(self, block=True, timeout=None):
        """Remove and return an item from the queue.

        If optional args block is true and timeout is None (the default), block
        if necessary until an item is available."""
        if block:
            item = self.__db.blpop(self.key, timeout=timeout)
        else:
            item = self.__db.lpop(self.key)

        if item:
            item = item[1]
        return item

    def get_nowait(self):
        """Equivalent to get(False)."""
        return self.get(False)


class RedisQueueReader(object):
    """
    This class is designed to return command from redis queue
    """
    def __init__(self, commands_queue, emergency_queue,  **redis_kwargs):

        self.logger = getLogger(type(self).__name__)
        self.commands_queue = RedisQueue(commands_queue, **redis_kwargs)
        self.emergency_queue = RedisQueue(emergency_queue, **redis_kwargs)

    def __iter__(self):
        return self

    def clean_queue(self):
        """
        No need to read old packets saved in queue before station is started.
        This method just reads everething and removes from queue.
        """
        self.logger.info("Running Cleanup")
        while not self.emergency_queue.empty():
            emergency_command = self.emergency_queue.get()
            self.logger.info("Cleaning Emergency Queue: {emergency_command}".format(command_json=command_json))

        while not self.commands_queue.empty():
            command_json = self.commands_queue.get().decode('utf-8')
            self.logger.info("Cleaning Commands Queue: {command_json}".format(command_json=command_json))

    def __next__(self):
        while True:
            if not self.emergency_queue.empty():
                emergency_command = self.emergency_queue.get()
                self.logger.info("Emergency Command = {emergency_command}".format(emergency_command=emergency_command))
                return "emergency_stop"

            elif not self.commands_queue.empty():
                command_json = self.commands_queue.get().decode('utf-8')
                self.logger.info("Command = {command_json}".format(command_json=command_json))
                return command_json
            else:
                return "idle"
