"""pytest configuration for the unit tests."""
import pytest


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
    return bn


@pytest.fixture()
def alice_sec_key_data(datadir):
    key_data = datadir.read('alice@openpgp.example.sec.asc')
    return key_data


@pytest.fixture()
def bob_pub_key_data(datadir):
    key_data = datadir.read('bob@openpgp.example.pub.asc')
    return key_data
