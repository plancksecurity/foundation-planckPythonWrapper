# -*- coding: utf-8 -*-
"""Message unit tests."""

from . import constants


def test_msg_enc_dec_roundtrip(pEp, import_ident_alice_as_own_ident, import_ident_bob):
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
    assert str(enc_msg.from_) == constants.ALICE_NAME_ADDR
    assert str(enc_msg.to[0]) == constants.BOB_NAME_ADDR
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
    assert key_list[0] == key_list[1] == constants.ALICE_FPR
    assert key_list[-1] == constants.BOB_FPR
    assert dec_msg.shortmsg == constants.SUBJECT
    assert dec_msg.longmsg.replace("\r", "") == msg.longmsg
    dec_lines = str(dec_msg).replace("\r", "").split("\n")
    # pEp version 2.2 seems to have fixed some of the replaced characters.
    # and changed also:
    # Content-Type: doesn't pring `; charset="utf-8"` anymore.
    # Content-Transfer-Encoding: doesn't print `quoted-printable` anymore.
    # Content-Disposition: is not present anymore.
    # `!` is not replaced by `=21` anymore.
    expected_dec_lines = \
"""From: Alice Lovelace <alice@openpgp.example>
To: Bob Babagge <bob@openpgp.example>
Subject: This is a subject
X-pEp-Version: 2.1
X-EncStatus: reliable
X-KeyList:
 X,X,D1A66E1A23B182C9980F788CFBFCC82A015E7330
MIME-Version: 1.0
Content-Type: text/plain
Content-Transfer-Encoding: 7bit

Hi world!
""".split("\n")
    assert dec_lines[:5] == expected_dec_lines[:5]
    assert dec_lines[7:] == expected_dec_lines[7:]


def test_msg_len_changes(pEp, import_ident_alice_as_own_ident, import_ident_bob):
    """Test that the original message is modified after encryption.

    Headers are added and therefore the modified unencrypted message length
    is different to the original.
    XXX: The original message should be left unchanged.
         There could be another method previous to `encrypt` that adds the
         extra headers and modify the subject returning a new message.

    """
    alice = import_ident_alice_as_own_ident
    bob = import_ident_bob

    msg = pEp.outgoing_message(alice)
    msg.to = [bob]
    msg.shortmsg = constants.SUBJECT
    msg.longmsg = constants.BODY
    msg_len = len(str(msg))
    # Encrypt Message
    msg.encrypt()

    # After encryption, the original message is modified!!
    # It contains one more header and the alice's public key, if it's the first
    # msg to bob.
    # XXX: if/when this is fixed, change the following `!=` to `==`
    msg_after_encrypt_len = len(str(msg))
    assert msg.shortmsg != constants.SUBJECT
    assert msg.longmsg == constants.BODY
    assert msg_after_encrypt_len != msg_len


def test_dec_msg_len(pEp, import_ident_alice_as_own_ident, import_ident_bob):
    """
    Test that the decrypted message length is different from the original.

    Because it adds extra headers.

    """
    alice = import_ident_alice_as_own_ident
    bob = import_ident_bob

    msg = pEp.outgoing_message(alice)
    msg.to = [bob]
    msg.shortmsg = constants.SUBJECT
    msg.longmsg = constants.BODY
    msg_len = len(str(msg))
    # Encrypt Message
    enc_msg = msg.encrypt()

    # Decrypt message.
    dec_msg, _key_list, _rating, _r = enc_msg.decrypt()
    dec_msg_len = len(str(dec_msg))

    assert dec_msg.longmsg.replace("\r", "") == constants.BODY  # msg.longmsg
    expected_dec_msg = \
"""From: Alice Lovelace <alice@openpgp.example>\r
To: Bob Babagge <bob@openpgp.example>\r
Subject: This is a subject\r
X-pEp-Version: 2.1\r
X-EncStatus: reliable\r
X-KeyList: \r
 EB85BB5FA33A75E15E944E63F231550C4F47E38E,EB85BB5FA33A75E15E944E63F231550C4F47E38E,D1A66E1A23B182C9980F788CFBFCC82A015E7330\r
MIME-Version: 1.0\r
Content-Type: text/plain\r
Content-Transfer-Encoding: 7bit\r
\r
Hi world!\r
"""
    assert expected_dec_msg == str(dec_msg)
    # The decrypted message length should then be equal to the original message
    # minus the extra headers added.
    dec_lines = str(dec_msg).split("\n")
    extra_headers_lines = dec_lines[3:7]
    extra_headers = "\n".join(extra_headers_lines) + "\n"
    len_extra_headers = len(extra_headers)
    print("len_extra_headers", len_extra_headers)
    assert dec_msg_len - len_extra_headers == msg_len


def test_null_char_rmed(pEp, import_ident_alice_as_own_ident, import_ident_bob):
    """Test that null characters and anything after them is removed."""
    alice = import_ident_alice_as_own_ident
    bob = import_ident_bob

    msg = pEp.outgoing_message(alice)
    msg.to = [bob]
    msg.shortmsg = constants.SUBJECT

    # Message with null chars, potentially for padding.
    body = "Hi Bob,\n" + "\0" * 255 + "\nBye,\nAlice."
    msg.longmsg = body
    # PYADAPT-91: The null characters and anything after them is removed.
    # If/when this is fixed, change the following assertion.
    assert msg.longmsg != body
