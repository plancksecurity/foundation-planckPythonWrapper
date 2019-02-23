# vim: set fileencoding=utf-8 :

# Sync test 2.0
# Copyleft 2018, 2019, p≡p foundation

# this file is under GNU General Public License 3.0


import pEp
import minimail


def messageToSend(msg):
    # this is assuming that msg is unencrypted; only true for beacons
    print("<!-- " + str(msg.from_) + " -->\n" + msg.attachments[0].decode())
    minimail.send(msg)


class UserInterface(pEp.UserInterface):
    def notifyHandshake(self, me, partner, signal):
        print("signal " + str(signal) + " for identities " + str(me) + " " + str(partner))


def run(path):
    me = pEp.Identity("alice@peptest.ch", path + " Neuman")
    pEp.myself(me)
    pEp.messageToSend = messageToSend
    ui = UserInterface()

