# -*- coding: utf-8 -*-
# This file is under GNU Affero General Public License 3.0
# see LICENSE.txt

"""Identity unit tests."""

import pytest

from . import constants
from . import model


# TODO: test_get_identity_by_{name,addr,etc..}
# def test_create_ident_myself(pEp, alice_myself):
# def test_create_ident_import(pEp, alice_myself):
# def test_create_ident_nokey(pEp, alice_myself):


def test_identity_constructor(pEp, model):
    alice = pEp.Identity(
        model.alice.addr,
        model.alice.name,
        model.alice.user_id
    )

    assert alice.address == model.alice.addr
    assert alice.username == model.alice.name
    assert alice.user_id == model.alice.user_id
    assert str(alice) == str(model.alice)


# Covers PYADPT-124
def test_identity_update_cpt(pEp,model):
    bob = pEp.Identity(model.bob.addr, model.bob.name)
    bob.update()
    assert bob.address == model.bob.addr
    assert bob.username == model.bob.name
    assert bob.user_id == 'TOFU_bob@peptest.org'
    assert bob.fpr == ''
    assert bob.comm_type == 0
    assert bob.lang == ''


# TODO:
# These here are actually plenty of individual tests
# Identity.update
# key_import
# set_own_key

@pytest.mark.skip(reason="needs to be decomposed and migrated to new data model")
def test_two_identities_succeed(pEp, model):
    alice = pEp.Identity(
        constants.ALICE_ADDRESS, constants.ALICE_USERNAME, '',
        constants.ALICE_FPR, 0, ''
    )
    assert alice.address == constants.ALICE_ADDRESS
    assert alice.username == constants.ALICE_USERNAME
    assert alice.fpr == constants.ALICE_FPR
    assert alice.user_id == ""
    assert alice.comm_type == 0
    assert alice.flags == 0

    pEp.import_key(model.bob.key_pub)

    bob = pEp.Identity()
    bob.address = constants.BOB_ADDRESS
    bob.username = constants.BOB_USERNAME
    bob.fpr = constants.BOB_FPR
    expected_bob = pEp.Identity(
        constants.BOB_ADDRESS, constants.BOB_USERNAME, '',
        constants.BOB_FPR, 56, ''
    )

    assert str(bob) == constants.BOB_NAME_ADDR
    assert bob.address == expected_bob.address
    assert bob.username == expected_bob.username
    assert bob.fpr == expected_bob.fpr
    assert bob.user_id == ""
    assert bob.comm_type == 0
    assert bob.flags == 0

    # Test that data after updating.
    bob.update()
    assert str(bob) == constants.BOB_NAME_ADDR
    assert bob.address == expected_bob.address
    assert bob.username == expected_bob.username
    assert bob.fpr == expected_bob.fpr
    assert bob.user_id == "TOFU_bob@openpgp.example"
    assert bob.comm_type == 56
    assert bob.flags == 0


@pytest.mark.skip(reason="needs to be decomposed and migrated to new data model")
def test_set_own_key(pEp, alice_key_sec):
    pEp.import_key(alice_key_sec)
    alice = pEp.Identity()
    alice.address = constants.ALICE_ADDRESS
    alice.username = constants.ALICE_USERNAME
    alice.fpr = constants.ALICE_FPR
    alice.user_id = constants.ALICE_NAME_ADDR

    expected_alice = pEp.Identity(
        constants.ALICE_ADDRESS, constants.ALICE_USERNAME, '',
        constants.ALICE_FPR, 0, ''
    )

    pEp.set_own_key(alice, alice.fpr)
    # assert str(alice) == constants.ALICE_NAME_ADDR
    assert str(alice) == str(expected_alice)
    assert alice.address == expected_alice.address
    assert alice.username == expected_alice.username
    # assert alice.user_id == constants.ALICE_NAME_ADDR
    assert alice.user_id == str(expected_alice)
    assert alice.fpr == expected_alice.fpr
    assert alice.comm_type == 255
    assert alice.flags == 0

    # After setting own key this would give ValueError: illegal value
    # alice.update()
