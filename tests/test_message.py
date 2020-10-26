"""Message unit tests."""
import os

from . import constants


def test_msg_enc_dec_roundtrip(tmpdir, alice_sec_key_data, bob_pub_key_data):
    os.environ["HOME"] = str(tmpdir)
    import pEp

    alice = pEp.Identity(
        constants.ALICE_ADDRESS, constants.ALICE_NAME,
        constants.ALICE_NAME_ADDR, constants.ALICE_FP, 0, ''
        )

    pEp.import_key(bob_pub_key_data)
    bob = pEp.Identity(
        constants.BOB_ADDRESS, constants.BOB_NAME, '',
        constants.BOB_FP, 56, ''
        )

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
    assert enc_msg.longmsg == \
        "this message was encrypted with p≡p https://pEp-project.org"

    # Decrypt message.
    dec_msg, key_list, rating, r = enc_msg.decrypt()
    assert r == 0
    # pEp version 2.2 throws this error:
    # AttributeError: module 'pEp' has no attribute 'PEP_rating'
    # assert rating == pEp.PEP_rating.PEP_rating_reliable
    # It seems to have changed to the following.
    assert rating == pEp.native_pEp.rating.reliable

    # The first 2 keys are Alice's ones, the last is Bob's one.
    assert key_list[0] == key_list[1] == constants.ALICE_FP
    assert key_list[-1] == constants.BOB_FP
    assert dec_msg.shortmsg == constants.SUBJECT
    assert dec_msg.longmsg.replace("\r", "") == msg.longmsg
    dec_lines = str(dec_msg).replace("\r", "").split("\n")
    # pEp version 2.2 seems to have fixed some of the replaced characters.
    # and changed also:
    # Content-Type: doesn't pring `; charset="utf-8"` anymore.
    # Content-Transfer-Encoding: doesn't print `quoted-printable` anymore.
    # Content-Disposition: is not present anymore.
    # `!` is not replaced by `=21` anymore.
    expected_dec_lines = """From: Alice Lovelace <alice@openpgp.example>
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
