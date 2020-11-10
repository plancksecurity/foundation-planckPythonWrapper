"""pytest configuration for the unit tests."""
import os
import pytest

from . import constants


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


@pytest.fixture(scope='function')
def tmpdir(tmpdir_factory, request):
    """Create a tmp dir for the tests"""
    base = str(hash(request.node.nodeid))[:3]
    bn = tmpdir_factory.mktemp(base)
    import os
    os.environ["HOME"] = str(bn)
    return bn


@pytest.fixture()
def alice_sec_key_data(datadir):
    key_data = datadir.read('alice@openpgp.example.sec.asc')
    return key_data


@pytest.fixture()
def bob_pub_key_data(datadir):
    key_data = datadir.read('bob@openpgp.example.pub.asc')
    return key_data


@pytest.fixture()
def create_alice_identity(tmpdir, alice_sec_key_data, bob_pub_key_data):
    os.environ["HOME"] = str(tmpdir)
    import pEp

    pEp.import_key(alice_sec_key_data)
    alice = pEp.Identity(
        constants.ALICE_ADDRESS, constants.ALICE_NAME,
        constants.ALICE_NAME_ADDR, constants.ALICE_FP, 0, ''
        )
    pEp.set_own_key(alice, constants.ALICE_FP)
    return alice


@pytest.fixture()
def create_bob_identity(tmpdir, bob_pub_key_data):
    os.environ["HOME"] = str(tmpdir)
    import pEp

    pEp.import_key(bob_pub_key_data)
    bob = pEp.Identity(
        constants.BOB_ADDRESS, constants.BOB_NAME, '',
        constants.BOB_FP, 56, ''
        )
    return bob
