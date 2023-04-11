# -*- coding: utf-8 -*-
# This file is under GNU Affero General Public License 3.0
# see LICENSE.txt

from . import utils

import pytest

@pytest.fixture()
def model():
    "Returns the whole data model"
    return Model()

identities = \
    {
        "alice": {
            "name": "alice",
            "user_id": "23",
            "accounts":
                {
                    "work": {
                        "addr": "alice_work@peptest.org",
                        "fpr": "3E45175EE953EBBEB948F11A6A03DB2A17FB9D15"
                    },
                    "home": {
                        "addr": "alice@peptest.org",
                        "fpr": "2D35731B9C754564CBAD15D2D18F7444594F2283"
                    }
                }
        },
        "bob": {
            "name": "bob",
            "user_id": "uuid:1-2-3-4",
            "accounts": \
                {
                    "work": {
                        "addr": "bob_work@peptest.org",
                        "fpr": "1A97F263D8319D6885F638C5AA81E1B5457A2B40"
                    },
                    "home": {
                        "addr": "bob@peptest.org",
                        "fpr": "6A9835699EF1215F1558A496D9C1D4B0984094E5"
                    }
                }
        }
    }

class Identity:
    """
    An Identity class that:
    - can represent pEp.Identity
    - is read-only (const)
    """

    def __init__(self, name="", user_id="", addr="", fpr="", key_sec="", key_pub=""):
        self.__name = name
        self.__user_id = user_id
        self.__addr = addr
        self.__fpr = fpr
        self.__key_sec = key_sec
        self.__key_pub = key_pub

    @property
    def name(self):
        return self.__name

    @property
    def user_id(self):
        return self.__user_id

    @property
    def addr(self):
        return self.__addr

    @property
    def fpr(self):
        return self.__fpr

    @property
    def key_sec(self):
        return self.__key_sec

    @property
    def key_pub(self):
        return self.__key_pub

    def debug(self) -> str:
        ret = "name:" + self.__name
        ret +="user_id:" + self.__user_id
        ret +="addr:" + self.__addr
        ret +="fpr:" + self.__fpr
        ret +="key_sec:" + self.__key_sec[0:255]
        ret +="key_pub:" + self.__key_pub[0:255]
        return ret

    def __str__(self):
        return "{} {}".format(self.name, "<{}>".format(self.addr))



# The Data Model
class Model:
    alice = None
    alice_work = None
    bob = None
    bob_work = None

    def getIdentity(self, name, account) -> Identity:
        # fetch keys for ident from data folder
        key_sec = utils.data_file_contents(identities[name]['accounts'][account]['fpr'] + ".sec.asc")
        key_pub = utils.data_file_contents(identities[name]['accounts'][account]['fpr'] + ".pub.asc")
        ident = Identity(name=identities[name]['name'],
                         user_id=identities[name]['user_id'],
                         addr=identities[name]['accounts'][account]['addr'],
                         fpr=identities[name]['accounts'][account]['fpr'],
                         key_pub=key_pub,
                         key_sec=key_sec
                         )
        return ident

    def __init__(self):
        self.alice = self.getIdentity("alice", "home")
        self.alice_work = self.getIdentity("alice", "work")

        self.bob = self.getIdentity("bob", "home")
        self.bob_work = self.getIdentity("bob", "work")
