'''
Errors that might be generated related to the socky module
'''

class SockyError(Exception):
    '''General Error related to socky'''

    _message = None
    _base_ex = None

    def __init__(self, message, base_ex=None):
        super(SockyError, self).__init__(message)
        self._message = message
        self._base_ex = base_ex

    def __str__(self):
        if not self._message:
            return 'Unknown Error'

        return self._message

    def __repr__(self):
        return 'SockyError(message="%s", base_ex="%r")' % (self._message, self._base_ex)

    message = property(fget=lambda self: self._message, doc='Error Message')
    base_ex = property(fget=lambda self: self._base_ex, doc='Base Exception (if any)')

__all__ = ['SockyError']
