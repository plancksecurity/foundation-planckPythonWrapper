#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
>>> import pEp
>>> me = pEp.Identity("alice.smith@peptest.ch", "Alice Smith", "23")
>>> me.username
'Alice Smith'
>>> print(me)
Alice Smith <alice.smith@peptest.ch>
>>> you = pEp.Identity("bob.bourne@peptest.ch", "Bob Bourne", "42")
>>> print(you)
Bob Bourne <bob.bourne@peptest.ch>
>>> m = pEp.outgoing_message(me)
>>> m.to = [you]
>>> m.shortmsg = "let's meet next week"
>>> m.longmsg = "Please call me back"
>>> m2 = m.encrypt()
>>> print(m2)
>>> m3, keys, rating, flags = m2.decrypt()
>>> rating
pEp.rating.reliable
"""

if __name__ == "__main__":
    import doctest
    doctest.testmod()
