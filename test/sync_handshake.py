#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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
from time import sleep

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
end_on = [
        pEp.sync_handshake_signal.SYNC_NOTIFY_ACCEPTED_DEVICE_ADDED,
        pEp.sync_handshake_signal.SYNC_NOTIFY_ACCEPTED_GROUP_CREATED,
        pEp.sync_handshake_signal.SYNC_NOTIFY_ACCEPTED_DEVICE_ACCEPTED,
    ]


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
    
    m = re.search("<keysync>(.*)</keysync>", msg.opt_fields["pEp.sync"].replace("\n", " "))
    if m:
        if etree:
            tree = objectify.fromstring(m.group(1).replace("\r", ""))
            text = etree.tostring(tree, pretty_print=True, encoding="unicode")
        else:
            text = m.group(1).replace("\r", "").strip()
            while text.count("  "):
                text = text.replace("  ", " ")
        print(text)


def messageToSend(msg):
    msg = add_debug_info(msg)
    minimail.send(inbox, msg, device_name)

def messageImapToSend(msg):
    import miniimap
    msg = add_debug_info(msg)
    miniimap.send('Inbox', msg)

def add_debug_info(msg):
    if msg.enc_format:
        m, keys, rating, flags = msg.decrypt(DONT_TRIGGER_SYNC)
    else:
        m = msg
    try:    
        text = "<!-- sending from " + device_name + " -->\n" + m.attachments[0].decode()
    except UnicodeDecodeError as e:
        text = "<!-- sending from " + device_name + " -->\n *** NO DECODER AVAILABLE FOR THIS MESSAGE TYPE ***\n" 
    output(text)
    msg.opt_fields = { "pEp.sync": text }
    return msg



def this_notifyHandshake(me, partner, signal):
    print(colored(str(signal), "yellow"), end=" ")
    output("on " + device_name + "" if not me.fpr else
           "for identities " + str(me.fpr) + " " + str(partner.fpr))
    if me.fpr and partner.fpr:
        assert me.fpr != partner.fpr

    if signal in (
        pEp.sync_handshake_signal.SYNC_NOTIFY_INIT_ADD_OTHER_DEVICE,
        pEp.sync_handshake_signal.SYNC_NOTIFY_INIT_ADD_OUR_DEVICE,
        pEp.sync_handshake_signal.SYNC_NOTIFY_INIT_FORM_GROUP
    ):
        if isinstance(end_on, list):
            end_on.extend([
                pEp.sync_handshake_signal.SYNC_NOTIFY_SOLE,
                pEp.sync_handshake_signal.SYNC_NOTIFY_IN_GROUP,
            ])
        sleep(.5) # user is reading message
        try:
            if not options.noanswer:
                if options.reject:
                    pEp.deliver_handshake_result(SYNC_HANDSHAKE_REJECTED)
                else:
                    pEp.deliver_handshake_result(SYNC_HANDSHAKE_ACCEPTED)
        except NameError:
            pEp.deliver_handshake_result(SYNC_HANDSHAKE_ACCEPTED)
    if signal in end_on:
        global the_end
        the_end = True


def shutdown_sync():
    pEp.shutdown_sync()


def run(name, color=None, imap=False, own_ident=1, leave=False):

    global device_name
    device_name = name
    pEp.notify_handshake = this_notifyHandshake

    if color:
        global output
        output = lambda x: print(colored(x, color))
        if color == "red":
            pEp.debug_color(31)
        elif color == "green":
            pEp.debug_color(32)
        elif color == "cyan":
            pEp.debug_color(36)

    if imap:
        import miniimap
        import imap_settings
        
        me = pEp.Identity(imap_settings.IMAP_EMAIL, name + " of " + imap_settings.IMAP_USER, name)
        pEp.myself(me)
        pEp.message_to_send = messageImapToSend
    else:
        me = pEp.Identity("alice@peptest.ch", name + " of Alice Neuman", name)
        pEp.myself(me)

        if own_ident >= 2:
            me2 = pEp.Identity("alice@pep.security", name + " of Alice Neuman", name)
            pEp.myself(me2)

        if own_ident == 3:
            me3 = pEp.Identity("alice@pep.foundation", name + " of Alice Neuman", name)
            pEp.myself(me3)    

        pEp.message_to_send = messageToSend

    if multithreaded:
        from threading import Thread
        def sync_thread():
            print(colored("********* ", "yellow") + colored("sync_thread entered", color))
            print(colored("********* ", "yellow") + colored("UserInterface object created", color))
            pEp.Sync.run()
            print(colored("********* ", "yellow") + colored("leaving sync_thread", color))
        sync = Thread(target=sync_thread)
        sync.start()
    else:
        pEp.start_sync();

    try:
        if leave:
            pEp.leave_device_group()

        while not the_end:
            if pEp.is_sync_active():
                pass # we could react on this
            if imap:
                l = miniimap.recv_all()
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
    optParser.add_option("--no-answer", action="store_true", dest="noanswer",
            help="do not answer device group handshake")
    optParser.add_option("-E", "--end-on", dest="notifications",
            help="end test on these notifications")
    optParser.add_option("-j", "--multi-threaded", action="store_true",
            dest="multithreaded",
            help="use multithreaded instead of single threaded implementation")
    optParser.add_option("-n", "--noend", action="store_true",
            dest="noend", help="do not end")
    optParser.add_option("-i", "--imap", action="store_true",
            dest="imap",
            help="use imap instead of minimail")
    optParser.add_option("-o", "--own-identities", type="int", dest="own_ident",
            help="simulate having OWN_IDENT own identities (1 to 3)", default=1)
    optParser.add_option("-L", "--leave-device-group", action="store_true",
            dest="leave",
            help="after a successful sync run this to make the device leave the "
            "device group again")

    options, args = optParser.parse_args()

    if not options.exec_for:
        options.exec_for = os.path.basename(os.getcwd())

    if options.own_ident < 1 or options.own_ident > 3:
        raise ValueError("illegal number of own identities (allowed are 1 to 3)")

    if options.notifications:
        end_on = eval(options.notifications)
        try: None in end_on
        except TypeError:
            end_on = (end_on,)

    if options.noend:
        end_on = (None,)

    if options.imap and options.own_ident >1:
        raise ValueError("Multiple own identities not supported for imap mode")        

    multithreaded = options.multithreaded
    run(options.exec_for, options.color, options.imap, options.own_ident, options.leave)
