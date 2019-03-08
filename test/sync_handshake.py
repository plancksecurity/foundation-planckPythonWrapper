# vim: set fileencoding=utf-8 :

# Sync test 2.0
# Copyleft 2018, 2019, p≡p foundation

# this file is under GNU General Public License 3.0


import pathlib
import pEp
import minimail


inbox = pathlib.Path("..") / "TestInbox"


def messageToSend(msg):
    # this is assuming that msg is unencrypted; only true for beacons
    print("<!-- " + str(msg.from_) + " -->\n" + msg.attachments[0].decode())
    minimail.send(inbox, msg)


class UserInterface(pEp.UserInterface):
    def notifyHandshake(self, me, partner, signal):
        print("signal " + str(signal) + " for identities " + str(me) + " " +
                str(partner))


def run(name):
    me = pEp.Identity("alice@peptest.ch", name + " of Alice Neuman")
    pEp.myself(me)
    pEp.messageToSend = messageToSend
    ui = UserInterface()

    try:
        while True:
            l = minimail.recv_all(inbox, name)
            for m in l:
                msg = pEp.Message(m)
                msg.decrypt()
    except KeyboardInterrupt:
        pass


if __name__=="__main__":
    from optparse import OptionParser

    optParser = OptionParser()
    optParser.description = "For debugging try: $ cd $DEV && lldb python3 -- " \
            + "sync_handshake.py -e $DEV"

    optParser.add_option("-e", "--exec-for", action="store", type="string",
            dest="exec_for", help="execute for name of simulated device")
    options, args = optParser.parse_args()

    if not options.exec_for:
        raise SyntaxError("--exec-for is mandatory, try --help")

    run(options.exec_for)

