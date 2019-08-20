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
import miniimap

import sync_settings as settings

from datetime import datetime

try:
    from termcolor import colored
except:
    colored = lambda x, y: x

try:
    from lxml import etree
    from lxml import objectify
except:
    etree = None


inbox = pathlib.Path("..") / "TestInbox"
device_name = ""
output = print
multithreaded = False

DONT_TRIGGER_SYNC = 0x200
SYNC_HANDSHAKE_ACCEPTED = 0
SYNC_HANDSHAKE_REJECTED = 1

the_end = False
end_on = (
        pEp.sync_handshake_signal.SYNC_NOTIFY_ACCEPTED_DEVICE_ADDED,
        pEp.sync_handshake_signal.SYNC_NOTIFY_ACCEPTED_GROUP_CREATED
    )


def print_msg(p):
    if isinstance(p, pathlib.Path):
        if p.name[:5] == "Phone":
            color = "red"
        elif p.name[:6] == "Laptop":
            color = "green"
        else:
            color = "cyan"
        with open(p, "r") as f:
            t = f.read(-1)
        msg = pEp.Message(t)
        print("\n" + colored(p.name, color))
        print(colored(str(datetime.fromtimestamp(p.stat().st_mtime)), color))
    elif isinstance(p, pEp.Message):
        msg = p
    else:
        raise TypeError("print_msg(): pathlib.Path and pEp.Message supported, but "
                + str(type(p)) + " delivered")
    
    m = False

    if msg.opt_fields.get("pEp.sync"):
        m = re.search("<keysync>(.*)</keysync>", msg.opt_fields["pEp.sync"].replace("\n", " "))
    
    if m:
        if etree:
            tree = objectify.fromstring(m.group(1).replace("\r", ""))
            text = etree.tostring(tree, pretty_print=True, encoding="unicode")
        else:
            text = m.group(1).replace("\r", "").strip()
            while text.count("  "):
                text = text.replace("  ", " ")
        print('-- BEACON --')
        print(text)


def messageToSend(msg):
    if msg.enc_format:
        m, keys, rating, flags = msg.decrypt(DONT_TRIGGER_SYNC)
    else:
        m = msg
    text = "<!-- sending from " + device_name + " -->\n" + m.attachments[0].decode()
    output(text)
    msg.opt_fields = { "pEp.sync": text }
    minimail.send(inbox, msg, device_name)

def messageImapToSend(msg):
    if msg.enc_format:
        m, keys, rating, flags = msg.decrypt(DONT_TRIGGER_SYNC)
    else:
        m = msg
    text = "<!-- sending from " + device_name + " -->\n" + m.attachments[0].decode()
    output(text)
    msg.opt_fields = { "pEp.sync": text }
    miniimap.send(inbox, msg)

def getMessageToSend(msg):
    if msg.enc_format:
        m, keys, rating, flags = msg.decrypt(DONT_TRIGGER_SYNC)
    else:
        m = msg
    text = "<!-- sending from " + device_name + " -->\n" + m.attachments[0].decode()
    output(text)
    msg.opt_fields = { "pEp.sync": text }
    return msg

class UserInterface(pEp.UserInterface):
    def notifyHandshake(self, me, partner, signal):
        output("on " + device_name + " signal " + str(signal) + " for identities " + str(me.fpr) + " " +
                str(partner.fpr))
        if me.fpr and partner.fpr:
            assert me.fpr != partner.fpr

        if signal in (
                pEp.sync_handshake_signal.SYNC_NOTIFY_INIT_ADD_OTHER_DEVICE,
                pEp.sync_handshake_signal.SYNC_NOTIFY_INIT_ADD_OUR_DEVICE,
                pEp.sync_handshake_signal.SYNC_NOTIFY_INIT_FORM_GROUP
            ):
            try:
                if options.reject:
                    self.deliverHandshakeResult(SYNC_HANDSHAKE_REJECTED)
                else:
                    self.deliverHandshakeResult(SYNC_HANDSHAKE_ACCEPTED)

            except NameError:
                self.deliverHandshakeResult(SYNC_HANDSHAKE_ACCEPTED)
        if signal in end_on:
            global the_end
            the_end = True


def shutdown_sync():
    pEp.shutdown_sync()


def run(name, color=None, imap=False):
    global device_name
    device_name = name

    if color:
        global output
        output = lambda x: print(colored(x, color))

    if imap:
        me = pEp.Identity(settings.IMAP_EMAIL, name + " of " + settings.IMAP_USER, name)
        pEp.myself(me)
        pEp.messageToSend = messageImapToSend
    else:
        me = pEp.Identity("alice@peptest.ch", name + " of Alice Neuman", name)
        pEp.myself(me)
        pEp.messageToSend = messageToSend
    


    if multithreaded:
        from threading import Thread
        def sync_thread():
            print(colored("********* ", "yellow") + colored("sync_thread entered", color))
            ui = UserInterface()
            print(colored("********* ", "yellow") + colored("UserInterface object created", color))
            pEp.do_sync_protocol()
            print(colored("********* ", "yellow") + colored("leaving sync_thread", color))
        sync = Thread(target=sync_thread)
        sync.start()
    else:
        sync = None
        ui = UserInterface()

    try:
        while not the_end:
            if imap:
                l = miniimap.recv_all(inbox, 'start_time')
            else:
                l = minimail.recv_all(inbox, name)
            for n, m in l:
                msg = pEp.Message(m)
                output("*** Reading")
                print_msg(msg)
                msg2, keys, rating, flags = msg.decrypt()

    except KeyboardInterrupt:
        shutdown_sync()
        sys.exit()


if __name__=="__main__":
    from optparse import OptionParser

    optParser = OptionParser()
    optParser.description = __doc__

    optParser.add_option("-e", "--exec-for", action="store", type="string",
            dest="exec_for", help="execute for name of simulated device " +
                    "(default: name of actual directory)")
    optParser.add_option("--color", action="store", type="string",
            dest="color", help="print debug output in this color", default=None)
    optParser.add_option("--reject", action="store_true", dest="reject",
            help="reject device group")
    optParser.add_option("--accept", action="store_false", dest="reject",
            help="accept device group (default)")
    optParser.add_option("-E", "--end-on", dest="notifications",
            help="end test on these notifications")
    optParser.add_option("-j", "--multi-threaded", action="store_true",
            dest="multithreaded",
            help="use multithreaded instead of single threaded implementation")
    options, args = optParser.parse_args()

    if not options.exec_for:
        options.exec_for = os.path.basename(os.getcwd())

    if options.notifications:
        end_on = eval(options.notifications)
        try: None in end_on
        except TypeError:
            end_on = (end_on,)

    multithreaded = options.multithreaded
    run(options.exec_for, options.color)

