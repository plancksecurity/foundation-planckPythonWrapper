#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from . import constants
import pytest

# """
# >>> import pEp
# >>> me = pEp.Identity("alice.smith@peptest.ch", "Alice Smith", "23")
# >>> me.username
# 'Alice Smith'
# >>> print(me)
# Alice Smith <alice.smith@peptest.ch>
# >>> you = pEp.Identity("bob.bourne@peptest.ch", "Bob Bourne", "42")
# >>> print(you)
# Bob Bourne <bob.bourne@peptest.ch>
# >>> m = pEp.outgoing_message(me)
# >>> m.to = [you]
# >>> m.shortmsg = "let's meet next week"
# >>> m.longmsg = "Please call me back"
# >>> m2 = m.encrypt()
# >>> print(m2)
# >>> m3, keys, rating, flags = m2.decrypt()
# >>> rating
# pEp.rating.reliable
# """
#
# if __name__ == "__main__":
#     import doctest
#     doctest.testmod()

def test_basic(pEp, model):
    me = pEp.Identity(
        model.alice.addr,
        model.alice.name,
        model.alice.user_id
    )
    assert me.username == model.alice.name
    assert str(me) == str(model.alice)
    you = pEp.Identity(
        model.bob.addr,
        model.bob.name,
        model.bob.user_id
    )
    assert str(you) == str(model.bob)
    #TODO: pEp.outgoing_message() needs to return type pEp.Message not None
    m = pEp.outgoing_message(me)
    m.to = [you]
    m.shortmsg = constants.SUBJECT
    m.longmsg = constants.BODY
    #TODO: encrypt needs to return message type
    m2 = m.encrypt()
    m3, keys, rating, flags = m2.decrypt()
    #TODO: fix pEp.rating
    # assert rating == pEp.
