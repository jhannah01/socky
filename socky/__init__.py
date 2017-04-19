'''
Wraps the Python socket module with extended functionality to provide support for
anonymized connectivity using SOCKS/Tor or HTTP proxies
'''

import sys
import imp

from socky.errors import SockyError
from socky.providers import SockyProvider, SOCKSProvider, TorSockyProvider, LoggerProvider

class SocketImporter(object):
    '''
    This class, when registered in sys.meta_path, will ensure all attempts
    to import the socket module will result in the caller receiving a
    monkey-patched version of socket.socket.
    '''

    _path = None
    _socky_instance = None
    _verbose = False

    def __init__(self, socky_instance, verbose=False):
        if not isinstance(socky_instance, SockyProvider):
            raise ValueError('socky_instance must be a subclass of SockyProvider')

        self._socky_instance = socky_instance
        self._verbose = verbose

    def find_module(self, fullname, path=None):
        '''
        If the fullname is 'socket' then we will need to handle loading/patching
        the module
        '''

        if fullname != 'socket':
            return None

        self._path = path
        return self

    def load_module(self, name):
        '''
        This method does the actual work of loading the required module
        as well as patching it
        '''

        if self._verbose:
            print '[--] Got import request for "socket". Wrapping..'

        mod = sys.modules.get('socket', None)
        if not mod:
            mod_info = imp.find_module('socket', self._path)
            mod = imp.load_module(name, *mod_info)

        if getattr(mod, '_is_wrapped', False):
            if self._verbose:
                print '[**] socket module is already wrapped. Passing loaded instance.'
            return mod

        real_socket = getattr(mod, 'socket')
        setattr(mod, '_unwrapped_socket', real_socket)
        setattr(mod, 'socket', self._socky_instance.socket)
        setattr(mod, '_is_wrapped', True)

        if self._verbose:
            print '[**] Monkey-patched socket.socket with provided instance.'

        return mod

def wrap_socket(socky_instance, verbose=False):
    '''
    Monkey-patches socket.socket method, replacing it with the corresponding method
    in the provided socky_instance. This method will also register a sys.meta_path module
    importer to ensure any future attempts to import socket (i.e. modules which import the
    method using "from socket import socket") will also receive the wrapped function.

    This should ensure that all currently loaded module as well as modules imported in the
    future are wrapped automatically. In order to revert this functionality, unwrap_socket
    must be called.

    Args:
        socky_instance (socky.SockyProvider): An instance of one of the implementations of
        socky.SockyProvider.
        verbose (bool): Determines if verbose output should be printed. Defaults to False
    '''

    has_importer = False

    for m_path in sys.meta_path:
        if isinstance(m_path, SocketImporter):
            has_importer = True
            break

    if not has_importer:
        if verbose:
            print '[--] Registering new sys.meta_path SocketImporter..'

        sys.meta_path.append(SocketImporter(socky_instance=socky_instance, verbose=verbose))

    mod = sys.modules.get('socket', None)

    if not mod:
        if verbose:
            print '[--] Attempting to load socket module'

        mod = __import__('socket')
        if not mod:
            raise SockyError('Unable to find imported socket module')
    else:
        if not getattr(mod, '_is_wrapped', False):
            if verbose:
                print '[--] Attempting to re-import socket module in order to wrap it'

            del sys.modules['socket']
            __import__('socket')
            mod = sys.modules.get('socket', None)

            if not mod:
                raise SockyError('Unable to find imported socket module')

            if not getattr(mod, '_is_wrapped', False):
                raise SockyError('Unable to wrap re-imported socket module')

    if verbose:
        print '[**] Successfully loaded and hooked socket.socket with provided socky_instance'

def unwrap_socket(verbose=False):
    '''
    Undoes the work on wrap_socket and also removes the module importer.
    This effectively reverts the socket.socket method back to the original one.
    '''

    sys.meta_path = [mp for mp in sys.meta_path if not isinstance(mp, SocketImporter)]

    mod = sys.modules.get('socket', None)
    if not mod:
        if verbose:
            print '[--] Cannot find socket module.'
        return

    if hasattr(mod, '_is_wrapped'):
        delattr(mod, '_is_wrapped')

    real_socket = getattr(mod, '_unwrapped_socket', None)
    if real_socket:
        if verbose:
            print '[--] Reverting socket.socket back to original method.'
        setattr(mod, 'socket', real_socket)
        delattr(mod, '_unwrapped_socket')


__version__ = '1.0.0'

__all__ = ['SocketImporter', 'wrap_socket', 'unwrap_socket', 'SOCKSProvider',
           'TorSockyProvider', 'LoggerProvider', 'SockyProvider']
