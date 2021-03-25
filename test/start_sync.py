#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pEp
import time
pEp.set_debug_log_enabled(True)

def msg2send(message):
    print("MSG2SEND")
    # print(message)

def handshake(me, partner, signal):
    print("HANDSHAKE")
    print(me.fpr)
    print(partner.fpr)
    print(signal)

pEp.message_to_send = msg2send
pEp.notify_handshake = handshake

alice = pEp.Identity("tedst@alice.com", "alice", "23")
pEp.myself(alice)
print(alice.fpr)

while True:
    print("start_sync()")
    pEp.start_sync()
    print("Running...")
    time.sleep(3)

    print("shutdown_sync()")
    pEp.shutdown_sync()
    print("END")
    time.sleep(3)

