'''
Providers a SOCKS-backed socket based on the provided host and port information
'''

import socks
from enum import Enum

from socky.providers import SockyProvider


class SOCKSTypes(Enum):
    '''
    Enumeration of the possible proxy types supported (these simply expose
    the underlying PySocks types)
    '''

    SOCKS4 = socks.SOCKS4
    SOCKS5 = socks.SOCKS5
    HTTP = socks.HTTP

class SOCKSProvider(SockyProvider):
    '''
    The Socky provider which augments a standard socket.socket instance to pass traffic through
    the specified SOCKS host
    '''

    _host = None
    _port = None
    _credentials = ()
    _proxy_type = SOCKSTypes.SOCKS5
    _remote_dns = True

    def __init__(self, host, port, credentials=None, proxy_type=SOCKSTypes.SOCKS5,
                 remote_dns=True, name='socks', verbose=False):
        super(SOCKSProvider, self).__init__(name, verbose=verbose)

        if credentials:
            if isinstance(credentials, (tuple, list)) and len(credentials) == 2:
                self._credentials = credentials
            elif isinstance(credentials, dict):
                if ('username' not in credentials) or ('password' not in credentials):
                    raise ValueError('Invalid credentials provided. Must be a tuple, list or\
                                     dictionary with the keys "username" and "password"')
                self._credentials = (credentials['username'], credentials['password'])
            else:
                raise ValueError('Invalid credentials provided: %r' % credentials)

        if not proxy_type:
            proxy_type = socks.SOCKS5
        elif isinstance(proxy_type, SOCKSTypes):
            proxy_type = proxy_type.value
        else:
            raise ValueError('Invalid proxy_type provided: %r' % proxy_type)

        self._host = host
        self._port = int(port)
        self._proxy_type = proxy_type
        self._remote_dns = remote_dns

    def socket(self, *args, **kwargs):
        sock = socks.socksocket(*args, **kwargs)
        sock.set_proxy(socks.SOCKS5, self._host, self._port)

        if self.verbose:
            print '[--] Setup SOCKS-backed socket (host: %s, port: %d)' % (self._host, self._port)

        return sock

    host = property(fget=lambda self: self._host, doc='SOCKS Hostname/IP')
    port = property(fget=lambda self: self._port, doc='SOCKS Port')
    credentials = property(fget=lambda self: self._credentials, doc='Proxy Credentials')
    proxy_type = property(fget=lambda self: self._proxy_type, doc='Proxy Type')
    remote_dns = property(fget=lambda self: self._remote_dns, doc='Use remote DNS')

__all__ = ['SOCKSProvider']
