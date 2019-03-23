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
import sys
import re
import pEp
import minimail

from datetime import datetime

try:
    from termcolor import colored
except:
    colored = lambda x, y: x


inbox = pathlib.Path("..") / "TestInbox"
device_name = ""
output = print

DONT_TRIGGER_SYNC = 0x200
SYNC_HANDSHAKE_ACCEPTED = 0


def print_msg(p):
    if p.name[:5] == "Phone":
        color = "red"
    elif p.name[:6] == "Laptop":
        color = "green"
    else:
        color = None
    with open(p, "r") as f:
        t = f.read(-1)
    msg = pEp.Message(t)
    print("\n" + colored(p.name, color))
    print(datetime.fromtimestamp(p.stat().st_mtime))
    m = re.search("<payload>(.*)</payload>", msg.opt_fields["pEp.sync"])
    print(m.group(1))


def messageToSend(msg):
    if msg.enc_format:
        m, keys, rating, flags = msg.decrypt(DONT_TRIGGER_SYNC)
    else:
        m = msg
    text = "<!-- sending from " + device_name + " -->\n" + m.attachments[0].decode()
    output(text)
    msg.opt_fields = { "pEp.sync": text }
    minimail.send(inbox, msg, device_name)


class UserInterface(pEp.UserInterface):
    def notifyHandshake(self, me, partner, signal):
        output("on " + device_name + " signal " + str(signal) + " for identities " + str(me.fpr) + " " +
                str(partner.fpr))

        self.deliverHandshakeResult(SYNC_HANDSHAKE_ACCEPTED)


def run(name, color=None):
    global device_name
    device_name = name

    if color:
        global output
        output = lambda x: print(colored(x, color))

    me = pEp.Identity("alice@peptest.ch", name + " of Alice Neuman", name)
    pEp.myself(me)
    pEp.messageToSend = messageToSend
    ui = UserInterface()

    try:
        while True:
            l = minimail.recv_all(inbox, name)
            for m in l:
                msg = pEp.Message(m)
                msg2, keys, rating, flags = msg.decrypt()
                #text = "<!-- receiving on " + device_name + " -->\n" + msg2.attachments[0].decode()
                #output(text)

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
            dest="color", help="print debug output in this color", default=None)
    options, args = optParser.parse_args()

    if not options.exec_for:
        options.exec_for = os.path.basename(os.getcwd())

    run(options.exec_for, options.color)

