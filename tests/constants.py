# -*- coding: utf-8 -*-
"""Constants for unit tests."""


# XXX: Create these first constants as part of the adapter
OUTGOING_MSG = 1
INCOMING_MSG = 2

ANGLE_ADDR = "<{}>"
NAME_ADDR = "{} {}"

ALICE_USERNAME = "Alice Lovelace"
ALICE_ADDRESS = "alice@openpgp.example"
ALICE_ID = 23
ALICE_FPR = "EB85BB5FA33A75E15E944E63F231550C4F47E38E"
ALICE_NAME_ADDR = NAME_ADDR.format(ALICE_USERNAME, ANGLE_ADDR.format(ALICE_ADDRESS))

BOB_USERNAME = "Bob Babagge"
BOB_ADDRESS = "bob@openpgp.example"
BOB_ID = 23
BOB_FPR = "D1A66E1A23B182C9980F788CFBFCC82A015E7330"
BOB_NAME_ADDR = NAME_ADDR.format(BOB_USERNAME, ANGLE_ADDR.format(BOB_ADDRESS))

SUBJECT = "This is a subject"
BODY = "Hi world!\n"
