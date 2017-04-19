'''
Provider for logging to a standard Python log handler in order to debug
modules calling socket.socket and socket.connect
'''

import sys
import logging

from socky.providers import SockyProvider

class LoggerProvider(SockyProvider):
    '''
    Logs calls to socket.socket and socket.connect for debugging module network
    connectivity
    '''

    _logger = None

    def __init__(self, logger=None):
        super(LoggerProvider, self).__init__('logger')

        if not logger:
            logger = logging.getLogger(__name__)
            logger.setLevel(logging.DEBUG)

            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

            ch = logging.StreamHandler()
            ch.setLevel(logging.DEBUG)
            ch.setFormatter(formatter)
            logger.addHandler(ch)

        self._logger = logger

    def socket(self, *args, **kwargs):
        self._logger.info('In socket.socket: (args: *%r, **%r)' % (args, kwargs))
        sock = self.get_real_socket(*args, **kwargs)

        # Add logic to wrap calls to socket._socketobject.connect

        return sock

    logger = property(fget=lambda self: self._logger, doc='Provided or generated logger')

__all__ = ['LoggerProvider']
