#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pEp
import time

def message_to_send(msg):
    print("User defined message_to_send() called")
    m, keys, flags = msg.decrypt()
    try:
        print(m.attachments[0].decode())
    except UnicodeDecodeError as e:
        print("decode failed")

def notify_handshake(me, partner, signal):
    print("User defined notify_handshake() called")
    print(me)
    print(partner)
    print(signal)

def start_stop_sync(duration):
    pEp.start_sync()
    time.sleep(duration)
    pEp.shutdown_sync()


alice = pEp.Identity("test@alice.com", "alice", "23")
pEp.myself(alice)
print(alice.fpr)

dir(pEp)

# test default callback
start_stop_sync(1)

# test user defined callback
pEp.message_to_send = message_to_send
# pEp.notify_handshake = notify_handshake

start_stop_sync(1)

# pEp.start_sync()
# while(True):
#     print("is_sync_active: {}".format(pEp.is_sync_active()))
#     time.sleep(3)
#     pEp.key_reset_all_own_keys()
#     time.sleep(3)
