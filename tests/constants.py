# -*- coding: utf-8 -*-
"""Constants for unit tests."""


# XXX: Create these first constants as part of the adapter
OUTGOING_MSG = 1
INCOMING_MSG = 2

ANGLE_ADDR = "<{}>"
NAME_ADDR = "{} {}"

BOB_NAME = "Bob Babagge"
BOB_ADDRESS = "bob@openpgp.example"
BOB_FP = "D1A66E1A23B182C9980F788CFBFCC82A015E7330"
BOB_NAME_ADDR = NAME_ADDR.format(BOB_NAME, ANGLE_ADDR.format(BOB_ADDRESS))

ALICE_NAME = "Alice Lovelace"
ALICE_ADDRESS = "alice@openpgp.example"
ALICE_FP = "EB85BB5FA33A75E15E944E63F231550C4F47E38E"
ALICE_NAME_ADDR = NAME_ADDR.format(ALICE_NAME, ANGLE_ADDR.format(ALICE_ADDRESS))

SUBJECT = "This is a subject"
BODY = "Hi world!\n"
