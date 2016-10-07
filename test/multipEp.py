import os
import sys
import multiprocessing
import importlib
import tempfile
import time
from collections import OrderedDict

# per-instance globals
pEp = None
handler = None
own_addresses = []
indent = 0
i_name = ""
handshakes_pending = []
handshakes_to_accept = []

def create_account(address, name):
    global own_addresses
    i = pEp.Identity(address, name)
    pEp.myself(i)
    own_addresses.append(address)

def printi(*args):
    global indent
    print(i_name + ">" * indent, *args)

def printheader(blah=None):
    global indent
    if blah is None:
        printi("-" * 80)
        indent = indent - 1
    else:
        indent = indent + 1
        printi("-" * (39 - int(len(blah)/2))  + 
               " " + blah + " " + 
               "-" * (39 - len(blah) + int(len(blah)/2)))

def printmsg(msg):
    printi("from :", msg.from_)
    printi("to :", msg.to)
    printi("recv :", msg.recv)
    printi("sent :", msg.sent)
    printi("short :", msg.shortmsg)
    printi("opt_fields :", msg.opt_fields)
    lng = msg.longmsg.splitlines()
    lngcut = lng[:20]+["[...]"] if len(lng)>20 else lng
    pfx = "long : "
    for l in lngcut :
        printi(pfx + l)
        pfx = "       "
    printi("attachments : ", msg.attachments)

def pEp_instance_run(iname, conn, msgs_folders, handshakes_seen, handshakes_validated):
    global pEp, handler, own_addresses, i_name

    i_name = iname

    pEp = importlib.import_module("pEp")

    class Handler(pEp.SyncMixIn):
        def messageToSend(self, msg):
            printheader("SYNC MESSAGE to send")
            printmsg(msg)
            printheader()
            for rcpt in msg.to + msg.cc + msg.bcc:
                # list inside dict from MP manager are not proxified.
                msgs = msgs_folders.get(rcpt.address,[])
                msg.sent = int(time.time())
                msgs.append(str(msg))
                msgs_folders[rcpt.address] = msgs

        def showHandshake(self, me, partner):
            printheader("show HANDSHAKE dialog")
            printi("handshake needed between " + repr(me) + " and " + repr(partner))
            tw = pEp.trustwords(me, partner, 'en')
            printi(tw)
            if tw in handshakes_seen :
                handshakes_seen.remove(tw)
                handshakes_to_accept.append((tw,partner))
                printi("--> TO ACCEPT (already seen)")
            else:
                handshakes_pending.append((tw,partner))
                handshakes_seen.append(tw)
            printheader()

            # TODO: reject scenario ?

    handler = Handler()

    while True:
        order = conn.recv()
        if order is None:
            break

        func, args, kwargs, timeoff = order[0:] + [None, [], {}, 0][len(order):]

        printheader("DECRYPT messages")
        # decrypt every non-consumed message for all instance accounts
        for own_address in own_addresses:
            msgs_for_me = msgs_folders[own_address]
            for msgstr in msgs_for_me:
                msg = pEp.incoming_message(msgstr)
                printi("--- decrypt()")
                msg.recv = int(time.time() + timeoff)
                printmsg(msg)
                msg2, keys, rating, consumed, flags = msg.decrypt()

                if consumed == "MESSAGE_CONSUMED":
                    printi("--- PEP_MESSAGE_CONSUMED")
                    # folder may have changed in the meantime,
                    # remove item directly from latest version of it.
                    folder = msgs_folders[own_address]
                    folder.remove(msgstr)
                    msgs_folders[own_address] = folder
                elif consumed == "MESSAGE_DISCARDED":
                    printi("--- PEP_MESSAGE_DISCARDED")
                else :
                    printi("->-", rating, "->-")
                    printmsg(msg2)
                    printi("---")
        printheader()

        if handshakes_pending:
            printheader("check pending handshakes accepted on other device")
            for tple in handshakes_pending:
                tw, partner = tple 
                if tw in handshakes_validated:
                    handshakes_validated.remove(tw)
                    handshakes_pending.remove(tple)
                    printi("ACCEPT pending handshake : "+ tw)
                    handler.deliverHandshakeResult(partner, 0)
            printheader()

        res = None
        if func is not None:
            printheader("Executing function " + func.__name__)
            printi("args :", args)
            printi("kwargs :", kwargs)
            res = func(*args,**kwargs)
            printi("function " + func.__name__ + " returned :", res)
            printheader()

        if handshakes_to_accept:
            printheader("apply to-accept-because-already-seen handshakes")
            for tple in handshakes_to_accept:
                tw, partner = tple 
                printi("ACCEPT handshake : "+ tw)
                handshakes_validated.append(tw)
                handshakes_to_accept.remove(tple)
                handler.deliverHandshakeResult(partner, 0)
            printheader()

        conn.send(res)

def pEp_instance_main(iname, *args):
    # run with a dispensable $HOME to get fresh DB and PGP keyrings
    with tempfile.TemporaryDirectory() as tmpdirname:
        print("Instance " + iname + " runs into " + tmpdirname)
        os.environ['HOME'] = tmpdirname
        pEp_instance_run(iname, *args)
        print(iname + " exiting")

def run_scenario(scenario):
    instances = OrderedDict()
    with multiprocessing.Manager() as manager:
        msgs_folders = manager.dict()
        handshakes_seen = manager.list()
        handshakes_validated = manager.list()
        for iname, order in scenario:
            if iname not in instances:
                conn, child_conn = multiprocessing.Pipe()
                proc = multiprocessing.Process(
                    target=pEp_instance_main,
                    args=(iname, child_conn, msgs_folders, 
                          handshakes_seen, handshakes_validated))
                proc.start()
                instances[iname] = (proc, conn)
                if "wait_for_debug" in sys.argv:
                    yes = input("#"*80 + "\n" +
                                "INSTANCE "  + iname + "\n" + 
                                "Enter y/yes/Y/YES to attach debugger to process "  + 
                                str(proc.pid) + "\nor just press ENTER\n" +
                                "#"*80 + "\n")
                    if yes in ["y", "Y", "yes" "YES"]:
                        # TODO : linux terminal support
                        #import subprocess
                        #subprocess.call(['xterm', '-e', 'lldb', '-p', str(proc.pid)])
                        import appscript
                        appscript.app('Terminal').do_script('lldb -p ' + str(proc.pid))
                        time.sleep(2)
            else:
                proc, conn = instances[iname]

            conn.send(order)
            res = conn.recv()

        if "wait_for_debug" in sys.argv:
            input("#"*80 + "\n" +
                  "Press ENTER to cleanup\n" +
                  "#"*80 + "\n")

        for iname, (proc, conn) in instances.items():
            # tell process to terminate
            conn.send(None)
            proc.join()

