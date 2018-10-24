# vim: set fileencoding=utf-8 :

# Sync test 2.0
# Copyleft 2018, Volker Birk

# this file is under GNU General Public License 3.0


import pEp


def messageToSend(msg):
    # this is assuming that msg is unencrypted; only true for beacons
    print("<!-- " + str(msg.from_) + " -->\n" + msg.attachments[0].decode())

pEp.messageToSend = messageToSend


class UserInterface(pEp.UserInterface):
    def notifyHandshake(self, me, partner, signal):
        print("signal " + str(signal) + " for identities " + str(me) + " " + str(partner))


ui = UserInterface()

