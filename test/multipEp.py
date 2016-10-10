import os
import sys
import multiprocessing
import importlib
import tempfile
import time
import types
from copy import deepcopy
from collections import OrderedDict

# manager globals
instances = None

# per-instance globals
pEp = None
handler = None
own_addresses = []
indent = 0
i_name = ""
handshakes_pending = []
handshakes_to_accept = []

# both side globals (managed by MP)
handshakes_seen = []
handshakes_validated = []
msgs_folders = None

def create_account(address, name):
    global own_addresses
    i = pEp.Identity(address, name)
    pEp.myself(i)
    own_addresses.append(address)

def _send_message(address, msg):
    global msgs_folders
    # list inside dict from MP manager are not proxified.
    msgs = msgs_folders.get(address,[])
    msg.sent = int(time.time())
    msgs.append(str(msg))
    msgs_folders[address] = msgs

def _encrypted_message(from_address, to_address, shortmsg, longmsg):
    m = pEp.outgoing_message(Identity(from_address, from_address))
    m.to = [pEp.Identity(to_address, to_address)]
    m.shortmsg = shortmsg
    m.longmsg = longmsg
    m.encrypt()
    return msg

def encrypted_message(from_address, to_address, shortmsg, longmsg):
    return str(_encrypted_message(from_address, to_address, shortmsg, longmsg))

def send_message(from_address, to_address, shortmsg, longmsg):
    msg = _encrypted_message(from_address, to_address, shortmsg, longmsg)
    _send_message(to_address, msg)

def decrypt_message(msgstr):
    msg = pEp.incoming_message(msgstr)
    msg2, keys, rating, consumed, flags = msg.decrypt()

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

def execute_order(order, handler, conn):
    global handshakes_pending, handshakes_to_accept, handshakes_seen
    global handshakes_validated, msgs_folders
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

def pEp_instance_run(iname, conn, _msgs_folders, _handshakes_seen, _handshakes_validated):
    global pEp, handler, own_addresses, i_name, msgs_folders
    global handshakes_pending, handshakes_to_accept
    global handshakes_seen, handshakes_validated

    # assign instance globals
    msgs_folders = _msgs_folders
    handshakes_seen = _handshakes_seen
    handshakes_validated = _handshakes_validated
    i_name = iname

    pEp = importlib.import_module("pEp")

    class Handler(pEp.SyncMixIn):
        def messageToSend(self, msg):
            printheader("SYNC MESSAGE to send")
            printmsg(msg)
            printheader()
            for rcpt in msg.to + msg.cc + msg.bcc:
                _send_message(rcpt.address, msg)

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

    handler = Handler()

    while True:
        order = conn.recv()
        if order is None:
            break

        execute_order(order, handler, conn)

    msgs_folders = None

def pEp_instance_main(iname, *args):
    # run with a dispensable $HOME to get fresh DB and PGP keyrings
    with tempfile.TemporaryDirectory() as tmpdirname:
        print("Instance " + iname + " runs into " + tmpdirname)
        os.environ['HOME'] = tmpdirname
        pEp_instance_run(iname, *args)
        print(iname + " exiting")

def run_instance_action(action):
    global handshakes_seen, handshakes_validated, msgs_folders
    global instances
    iname, order = action
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
    return conn.recv()

def purge_instance():
    global instances
    for iname, (proc, conn) in instances.items():
        # tell process to terminate
        conn.send(None)
        proc.join()

def run_manager_action(action):
    func, args, kwargs = action[0:] + (None, [], {})[len(action):]
    return func(*args, **kwargs)

def run_scenario(scenario):
    global handshakes_seen, handshakes_validated, msgs_folders, instances
    instances = OrderedDict()
    with multiprocessing.Manager() as manager:
        msgs_folders = manager.dict()
        handshakes_seen = manager.list()
        handshakes_validated = manager.list()

        res = None
        for action in scenario:
            output = None
            if type(action[-1]) == types.FunctionType:
                output = action[-1]
                action = action[:-1]

            if type(action[0]) == str:
                res = run_instance_action(action)
            else:
                res = run_manager_action(action)

            if output is not None:
                output(res, action)

        if "wait_for_debug" in sys.argv:
            input("#"*80 + "\n" +
                  "Press ENTER to cleanup\n" +
                  "#"*80 + "\n")

        purge_instance()

def cycle_until_no_change(*instancelist, maxcycles=20):
    count = 0
    while True:
        global msgs_folders
        tmp = deepcopy(dict(msgs_folders))
        for iname in instancelist:
            action = (iname, [])
            run_instance_action(action)
        count += 1

        if dict(msgs_folders) == tmp:
            return

        if count >= maxcycles:
            raise Exception("Too many cycles waiting for stability") 
    

