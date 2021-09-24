#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
>>> import pEp
>>> def message_to_send(msg):
...   m, keys, flags = msg.decrypt()
...   try:
...     m.attachments[0].decode()
...     print("decode successfull")
...   except UnicodeDecodeError as e:
...     print("decode failed")
>>> pEp.message_to_send = message_to_send
>>> pEp.myself(pEp.Identity(""))
>>> pEp.key_reset_all_own_keys()
decode successfull
decode successfull
decode successfull
"""

if __name__ == "__main__":
    import doctest
    doctest.testmod()
