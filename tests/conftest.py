# -*- coding: utf-8 -*-
"""pytest configuration for the unit tests."""

import os
import pytest

from . import constants

# Static Data
@pytest.fixture()
def datadir(request):
    """Get, read, open test files from the tests "data" directory."""
    class D:
        def __init__(self, basepath):
            self.basepath = basepath

        def open(self, name, mode="r"):
            return self.basepath.join(name).open(mode)

        def join(self, name):
            return self.basepath.join(name).strpath

        def read(self, name):
            with self.open(name, "r") as f:
                return f.read()

        def readlines(self, name):
            with self.open(name, "r") as f:
                return f.readlines()
    return D(request.fspath.dirpath("data"))

@pytest.fixture()
def alice_key_sec(datadir):
    key_data = datadir.read('alice@openpgp.example.sec.asc')
    return key_data

@pytest.fixture()
def bob_key_pub(datadir):
    key_data = datadir.read('bob@openpgp.example.pub.asc')
    return key_data

# Init
@pytest.fixture()
def env_init(tmpdir_factory, request):
    """Create a tmp dir for the tests"""
    base = str(abs(hash(request.node.nodeid)))[:3]
    bn = tmpdir_factory.mktemp(base)
    print(bn)
    import os
    os.environ["PEP_HOME"] = str(bn)
    os.environ["HOME"] = str(bn)

@pytest.fixture()
def pEp(env_init):
    import pEp
    return pEp

# Identities
@pytest.fixture()
def import_ident_alice(pEp, alice_key_sec):
    pEp.import_key(alice_key_sec)
    alice = pEp.Identity(
        constants.ALICE_ADDRESS, constants.ALICE_NAME,
        constants.ALICE_NAME_ADDR, constants.ALICE_FPR, 0, ''
    )
    return alice

@pytest.fixture()
def import_ident_alice_as_own_ident(pEp, import_ident_alice):
    alice = import_ident_alice
    pEp.set_own_key(alice, constants.ALICE_FPR)
    return alice

@pytest.fixture()
def import_ident_bob(pEp, bob_key_pub):
    pEp.import_key(bob_key_pub)
    bob = pEp.Identity(
        constants.BOB_ADDRESS, constants.BOB_NAME, '',
        constants.BOB_FPR, 56, ''
    )
    return bob
