# -*- coding: utf-8 -*-
# This file is under GNU Affero General Public License 3.0
# see LICENSE.txt

"""pytest configuration for the unit tests."""

from .model import *

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


@pytest.fixture()
def alice_myself(pEp, model):
    alice = pEp.Identity(
        model.alice.addr,
        model.alice.name,
        model.alice.user_id
    )
    pEp.myself(alice)
    return alice


@pytest.fixture()
def alice_imported(pEp, model):
    pEp.import_key(model.alice.key_sec)
    alice = pEp.Identity(
        model.alice.addr,
        model.alice.name,
        model.alice.user_id
    )
    return alice


@pytest.fixture()
def import_ident_alice_as_own_ident(pEp, model, alice_imported):
    alice = alice_imported
    pEp.set_own_key(alice, model.alice.fpr)
    return alice


@pytest.fixture()
def import_ident_bob(pEp, model):
    keys, own_idents = pEp.import_key_with_fpr_return(model.bob.key_pub)
    bob = pEp.Identity(
        model.bob.addr,
        model.bob.name,
    )
    pEp.set_comm_partner_key(bob, keys[0])
    bob.update()
    return bob
