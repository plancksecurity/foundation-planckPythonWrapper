#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pEp
import time

def user_message_to_send(msg):
    print("User defined callback implementation")

def start_stop_sync(duration):
    pEp.start_sync()
    time.sleep(duration)
    pEp.shutdown_sync()

dir(pEp)
# test default callback
start_stop_sync(1)
# test user defined callback
pEp.message_to_send = user_message_to_send
start_stop_sync(1)

pEp.start_sync()
while(True):
    print("is_sync_active: {}".format(pEp.is_sync_active()))
    time.sleep(1)