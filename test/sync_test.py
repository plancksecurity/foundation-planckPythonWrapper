import codecs
from pEp import *

_msg = []
_me = None
_partner = None

class Handler(SyncMixIn):
    def messageToSend(self, msg):
        global _msg
        print("-" * 80)
        print(str(msg).replace("\r", ""))
        _msg.append(msg)

    def showHandshake(self, me, partner):
        print("handshake needed between " + repr(me) + " and " + repr(partner))
        global _me, _partner
        _me, _partner = (me, partner)


handler = Handler()


def process(path):
    with open(path, 'r') as f:
        text = f.read()
    return Message(text)


# this is an interactive test, so start it with python -i

