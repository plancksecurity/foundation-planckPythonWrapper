# -*- coding: utf-8 -*-
# This file is under GNU Affero General Public License 3.0
# see LICENSE.txt

"""Message unit tests."""

from . import constants


def test_msg_enc_dec_roundtrip(pEp, model, import_ident_alice_as_own_ident, import_ident_bob):
    alice = import_ident_alice_as_own_ident
    bob = import_ident_bob

    msg = pEp.Message(constants.OUTGOING_MSG, alice)
    msg.to = [bob]
    msg.shortmsg = constants.SUBJECT
    msg.longmsg = constants.BODY
    assert msg.enc_format == 0
    # XXX: No way to check MIME so far.

    # Test that creating the `Message` with `outgoing_message` is the same.
    msg2 = pEp.outgoing_message(alice)
    msg2.to = [bob]
    msg2.shortmsg = constants.SUBJECT
    msg2.longmsg = constants.BODY
    assert str(msg2) == str(msg)

    # Encrypt Message
    enc_msg = msg.encrypt()

    assert enc_msg.enc_format == 3
    assert str(enc_msg.from_) == str(model.alice)
    assert str(enc_msg.to[0]) == str(model.bob)
    assert enc_msg.shortmsg == "p≡p"
    assert enc_msg.longmsg == "this message was encrypted with p≡p https://pEp-project.org"

    # Decrypt message.
    dec_msg, key_list, rating, r = enc_msg.decrypt()
    assert r == 0
    # pEp version 2.2 throws this error:
    # AttributeError: module 'pEp' has no attribute 'PEP_rating'
    # assert rating == pEp.PEP_rating.PEP_rating_reliable
    # It seems to have changed to the following.
    assert rating == pEp._pEp.rating.reliable

    # The first 2 keys are Alice's ones, the last is Bob's one.
    assert key_list[0] == key_list[1] == model.alice.fpr
    assert key_list[-1] == model.bob.fpr
    assert dec_msg.shortmsg == constants.SUBJECT
    assert dec_msg.longmsg.replace("\r", "") == msg.longmsg
    dec_lines = str(dec_msg).replace("\r", "").split("\n")
    print(dec_lines)

