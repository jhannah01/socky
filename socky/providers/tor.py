'''
Tor-backed Socky provider that effectively wraps SOCKSProvider with the SOCKS host
configured in Tor.
'''

from stem import SocketError
from stem.connection import AuthenticationFailure
from stem.control import Controller, Listener

from socky.errors import SockyError
from socky.providers import SockyProvider
from socky.providers.socks5 import SOCKSProvider, SOCKSTypes

class TorSockyProvider(SockyProvider):
    '''
    Queries and interacts with running instance of Tor to determine the SOCKS host
    and port to use to pass traffic across the Onion network
    '''

    _controller = None
    _socks_provider = None

    def __init__(self, password, tor_port=9051, name='tor', verbose=False):
        super(TorSockyProvider, self).__init__(name, verbose=verbose)
        self.setup_tor(tor_port, password)

        listeners = self._controller.get_listeners(Listener.SOCKS)
        if not listeners:
            raise SockyError('Tor does not appear to be configured to allow SOCKS')

        if isinstance(listeners, tuple):
            listeners = [listeners]

        (host, port) = listeners[0]

        self._socks_provider = SOCKSProvider(host, port, name='tor-socks', verbose=verbose)

    def setup_tor(self, port, password):
        try:
            self._controller = Controller.from_port(port=port)
            self._controller.authenticate(password=password)
        except SocketError as ex:
            raise SockyError('Unable to create Tor-backed socket: %s' % str(ex), base_ex=ex)
        except AuthenticationFailure as ex:
            raise SockyError('Error authenticating to Tor: %s' % str(ex), base_ex=ex)

        return self._controller

    def socket(self, *args, **kwargs):
        sock = self._socks_provider.socket(*args, **kwargs)

        if self.verbose:
            print '[**] Built Tor-backed socket: %r' % sock

        return sock

    controller = property(fget=lambda self: self._controller, doc='Tor Controller')
    socks_provider = property(fget=lambda self: self._socks_provider, doc='Wrapped SOCKS Provider')

__all__ = ['TorSockyProvider']
