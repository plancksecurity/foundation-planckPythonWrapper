# pEp package
# This file is being exectued upon 'import pEp'
#
# __all__ could be used to limit the symbols exported when using from <pkg> import *


# Import all symbols EXCEPT the ones beginning with underscore into the current namespace
from native_pEp import *

# TODO: inter-pkg ref to make sure which native_pEp in sys.path gets loaded
# like: pEp.native_pEp
# import the module
import native_pEp


# Executed on module import
def init():
    print(init, "called")
    native_pEp._init_after_main_module()


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


# Executed when run as script
def main():
    print("I am being run as a script")


# MAIN
if __name__ == "__main__":
    main()
else:
    init()
