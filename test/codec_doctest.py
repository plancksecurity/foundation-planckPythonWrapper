"""
>>> import pEp
>>> def messageToSend(msg):
...   m, keys, rating, flags = msg.decrypt()
...   try:
...     m.attachments[0].decode()
...     print("decode successfull")
...   except UnicodeDecodeError as e:
...     print("decode failed")
>>> pEp.messageToSend = messageToSend
>>> pEp.key_reset_all_own_keys()
decode successfull
decode successfull
decode successfull
"""

if __name__ == "__main__":
    import doctest
    doctest.testmod()
