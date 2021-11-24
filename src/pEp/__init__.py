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

# __all__ could be used to limit the symbols exported when using from <pkg> import *
try:
    from .__version__ import version as __version__
except ImportError:
    import warnings

    warnings.warn("Error loading build-time defined __version__.py, trying setuptools now...")
    try:
        import setuptools_scm

        __version__ = setuptools_scm.get_version()
        del setuptools_scm
    except Exception:
        warnings.warn('could not determine %s package version' % __name__)
        __version__ = '0.0.dev0+unknown'

# Imports all symbols EXCEPT the ones beginning with underscore
from ._pEp import *

# import the native module into the current namespace because we also need to access the names beginning
# with an underscore (of _pEp), but we dont want to import them into this module
import pEp._pEp

# 3rd party imports
from threading import Thread, Barrier
from time import sleep


# Executed on module import
def init():
    # print(init, "called")
    _pEp._init_after_main_module()
    _pEp._session_init(True);


def start_sync() -> None:
    """starts the sync thread"""
    Sync.start_sync()


def shutdown_sync() -> None:
    """call this to shut down the sync thread"""
    Sync.shutdown_sync()
    # set_sync_mode(SyncModes.Off)


# def set_sync_mode(mode):
    # _pEp._set_sync_mode(mode)
    # if mode == SyncModes.Sync:
    #     Sync.shutdown_sync()
    # if mode == SyncModes.Async:
    #     Sync.start_sync()
    # if mode == SyncModes.Off:
    #     Sync.shutdown_sync()



def is_sync_active() -> bool:
    """True if sync is active, False otherwise"""
    return Sync.getInstance().is_alive()


def message_to_send(msg):
    """
    message_to_send(msg)
    override pEp.message_to_send(msg) with your own implementation
    this callback is being called when a p≡p management message needs to be sent
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
    """
    print("notify_handshake() - default callback\n")
    print("overwrite this method")


class Sync(Thread):
    __instance: 'Sync' = None
    barr = Barrier(2)

    def __init__(self):
        if Sync.__instance != None:
            raise Exception("singleton!")
        else:
            Sync.__instance = self
            Thread.__init__(self)

    @staticmethod
    def getInstance() -> 'Sync':
        if Sync.__instance == None:
            Sync()
        return Sync.__instance

    def run(self):
        """
        * Sync Thread
        * NOPE 1. Execute registered startup function
        register_sync_callbacks
            * 2. Create session for the sync thread (registers: messageToSend, _inject_sync_event, _ensure_passphrase)
            * 3. register_sync_callbacks() (registers: _notifyHandshake, _retrieve_next_sync_event)
        * 4. Enter Sync Event Dispatching Loop (do_sync_protocol())
        unregister_sync_callbacks
            * 5. unregister_sync_callbacks()
            * 6. Release the session
        * NOPE 7. Execute registered shutdown function
        """
        # TODO catch exception, and rethrow in start()
        # _pEp._register_sync_callbacks()
        _pEp._session_init(True)
        self.barr.wait()

        while _pEp._do_protocol_step():
            sleep(1)

        _pEp._unregister_sync_callbacks()

    def start(self):
        """
        * (1. Done on init(): ensure session for the main thread
             (registers: messageToSend, _inject_sync_event, _ensure_passphrase))
        * 2. Start the sync thread
        * 3. Defer execution until sync thread register_sync_callbacks() has returned
        * 4. TODO: Throw pending exception from the sync thread
        """
        Thread.start(self)
        self.barr.wait()
        # TODO: Throw exceptions from sync thread
        # _pEp._notifyHandshake_sync_start()
        # sleep(2)

    @staticmethod
    def start_sync():
        if not Sync.getInstance().is_alive():
            Sync.getInstance().start()

    @staticmethod
    def shutdown_sync():
        if Sync.__instance:
            if Sync.__instance.is_alive():
                _pEp._inject_sync_shutdown()
                Sync.__instance.join()
                Sync.__instance = None
                # _pEp._notifyHandshake_sync_stop()


init()
