# vim: set fileencoding=utf-8 :

"""start a handshake test for one simulated device

this is being started once per device by sync_test.py
you can use this manually for debugging purposes

For debugging try:

$ cd $DEV && HOME=$PWD lldb python3 -- ../sync_handshake.py -e $DEV

"""

# Sync test 2.0
# Copyleft 2018, 2019, p≡p foundation

# this file is under GNU General Public License 3.0


import pathlib
import os
import pEp
import minimail

try:
    from termcolor import colored
except:
    colored = lambda x, y: x


inbox = pathlib.Path("..") / "TestInbox"
device_name = ""
output = print


def messageToSend(msg):
    if msg.enc_format:
        m, keys, rating, flags = msg.decrypt()
    else:
        m = msg
    output("<!-- " + str(m.from_) + " -->\n" + m.attachments[0].decode())
    minimail.send(inbox, msg, device_name)


class UserInterface(pEp.UserInterface):
    def notifyHandshake(self, me, partner, signal):
        output("on " + device_name + " signal " + str(signal) + " for identities " + str(me.fpr) + " " +
                str(partner.fpr))


def run(name, color=None):
    global device_name
    device_name = name

    if color:
        global output
        output = lambda x: print(colored(x, color))

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
    optParser.description = __doc__

    optParser.add_option("-e", "--exec-for", action="store", type="string",
            dest="exec_for", help="execute for name of simulated device " +
                    "(default: name of actual directory)")
    optParser.add_option("--color", action="store", type="string",
            desct="color", help="print debug output in this color")
    options, args = optParser.parse_args()

    if not options.exec_for:
        options.exec_for = os.path.basename(os.getcwd())

    run(options.exec_for, options.color)

