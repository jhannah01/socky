'''
Provides the basic implementation shared between all socky provider types as well as those
individual implementations (Tor, SOCKS, HTTP/HTTPS, etcetera).
'''

import sys
import socket
import inspect
import types

class SockyProvider(object):
    '''
    Base class for all Socky provider types.

    This class is the heart of the extended functionality provided by socky and all
    providers must inherit from this class.

    Any custom providers should inherit (either directly or indirectly) from this class
    so the wrap methods work as expected. The stub methods defined in this class should
    provide an idea of the basic required functionality required of such custom providers.
    '''

    _name = None
    _verbose = False

    def __init__(self, name, verbose=False):
        '''
        Initializes the internals of the object.

        Args:
            name (str): The name for this Socky provider type (i.e. "tor")
            verbose (bool): Indicates if verbose information should be printed out.
            Defaults to False.
        '''

        self._name = name
        self._verbose = verbose

    def socket(self, *args, **kwargs):
        '''
        Socky providers must implement this method and the caller spec should match that
        of socket.socket. This provides for the opportunity for providers to inject their
        own extended implementation of socket.socket.
        '''

        raise NotImplementedError('Socky providers must implement the socket method')

    @classmethod
    def is_wrapped(cls):
        '''
        Checks if the _is_wrapped attribute is set in the socket module which
        indicates it was previously wrapped
        '''

        mod = sys.modules.get('socket', None)
        if not mod:
            return None

        return getattr(mod, '_is_wrapped', False)

    @classmethod
    def get_real_socket(cls):
        '''
        Returns the real socket.socket method even if the module is wrapped
        '''

        mod = sys.modules.get('socket', None)
        if not mod:
            return None

        if cls.is_wrapped():
            return getattr(mod, '_unwrapped_socket', None)

        return getattr(mod, 'socket')

    name = property(fget=lambda self: self._name, doc='The name of the provider')
    verbose = property(fget=lambda self: self._verbose, doc='Indicates if verbose messages\
                       should be printed')

from socky.providers.socks5 import SOCKSProvider
from socky.providers.tor import TorSockyProvider
from socky.providers.logger import LoggerProvider

__all__ = ['SockyProvider', 'SOCKSProvider', 'TorSockyProvider', 'LoggerProvider']
