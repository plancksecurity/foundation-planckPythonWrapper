# -*- coding: UTF-8 -*-
# pEp package
#
# The names that are in _pEp that do not begin with an underscore, will be be imported into, and "re-exported" from this module.
# They are defined in boost-python/C++, and are directly part of the pEpPythonAdapter API
# The names that are in _pEp that DO begin with an underscore, will not be imported into this module, but will be accessible like _pEp._underscore_function().
# They are not directly part of the pEpPythonAdapter API, and are meant to be wrapped in this module.
# Example:
# def underscore_function():
#     _pEp._underscore_function()
#
# __all__ could be used to limit the symbols exported when using from <pkg> import *
# TODO: Commented out until problems solved
# from pkg_resources import DistributionNotFound, get_distribution

# Imports all symbols EXCEPT the ones beginning with underscore
from ._pEp import *

# import the native module into the current namespace because we also need to access the names beginning
# with an underscore (of _pEp), but we dont want to import them into this module
import ._pEp

# TODO: Commented out until problems solved
# try:
#     __version__ = get_distribution(__name__).version
# except DistributionNotFound:
#     print("Package is not installed.")

# Executed on module import
def init():
    print(init, "called")
    _pEp._init_after_main_module()


def message_to_send(msg):
    """
    message_to_send(msg)
    override pEp.message_to_send(msg) with your own implementation
    this callback is being called when a p≡p management message needs to be sent
    GIL CAVEAT
    """
    print("message_to_send() - default callback\n")
    print("overwrite this method")


def notify_handshake(me, partner, signal):
    """
    notifyHandshake(self, me, partner)
        me              own identity
        partner         identity of communication partner
        signal          the handshake signal
    overwrite this method with an implementation of a handshake dialog
    GIL CAVEAT
    """
    print("message_to_send() - default callback\n")
    print("overwrite this method")


init()
