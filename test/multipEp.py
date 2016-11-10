import os
import sys
import multiprocessing
import importlib
import tempfile
import time
import types
import itertools
from copy import deepcopy
from collections import OrderedDict

# FIXME : move to main pEp module
# PEP_rating :
PEP_rating_undefined = 0
PEP_rating_cannot_decrypt = 1
PEP_rating_have_no_key = 2
PEP_rating_unencrypted = 3
PEP_rating_unencrypted_for_some = 4
PEP_rating_unreliable = 5
PEP_rating_reliable = 6
PEP_rating_trusted = 7
PEP_rating_trusted_and_anonymized = 8
PEP_rating_fully_anonymous = 9

PEP_rating_mistrust = -1,
PEP_rating_b0rken = -2,
PEP_rating_under_attack = -3

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

def flush_all_mails():
    global msgs_folders
    count = sum(map(len,msgs_folders.values()))
    msgs_folders.clear()
    return count

def _encrypted_message(from_address, to_address, shortmsg, longmsg):
    m = pEp.outgoing_message(pEp.Identity(from_address, from_address))
    m.to = [pEp.Identity(to_address, to_address)]
    m.shortmsg = shortmsg
    m.longmsg = longmsg
    return m.encrypt()

def encrypted_message(from_address, to_address, shortmsg, longmsg):
    return str(_encrypted_message(from_address, to_address, shortmsg, longmsg))

def send_message(from_address, to_address, shortmsg, longmsg):
    msg = _encrypted_message(from_address, to_address, shortmsg, longmsg)
    _send_message(to_address, msg)

def decrypt_message(msgstr):
    msg = pEp.incoming_message(msgstr)
    printi("--- decrypt()")
    msg.recv = int(time.time())
    printmsg(msg)
    msg2, keys, rating, consumed, flags = msg.decrypt()
    printi("->-", rating, "->-")
    printmsg(msg2)
    printi("---")
    return rating

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

def execute_order(order, handler):
    global handshakes_pending, handshakes_to_accept, handshakes_seen
    global handshakes_validated, msgs_folders, own_addresses

    func, args, kwargs, timeoff = order[0:] + [None, [], {}, 0][len(order):]

    printheader("DECRYPT messages")
    # decrypt every non-consumed message for all instance accounts
    for own_address in own_addresses:
        msgs_for_me = msgs_folders.get(own_address, [])
        for msgstr in msgs_for_me:
            msg = pEp.incoming_message(msgstr)
            printi("--- decrypt()")
            msg.recv = int(time.time() + timeoff)
            printmsg(msg)
            msg2, keys, rating, consumed, flags = msg.decrypt()

            if consumed == "MESSAGE_CONSUME":
                printi("--- PEP_MESSAGE_CONSUMED")
                # folder may have changed in the meantime,
                # remove item directly from latest version of it.
                folder = msgs_folders[own_address]
                folder.remove(msgstr)
                msgs_folders[own_address] = folder
            elif consumed == "MESSAGE_IGNORE":
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

    return res

def pEp_instance_run(iname, _own_addresses, conn, _msgs_folders, _handshakes_seen, _handshakes_validated):
    global pEp, handler, own_addresses, i_name, msgs_folders
    global handshakes_pending, handshakes_to_accept
    global handshakes_seen, handshakes_validated

    # assign instance globals
    own_addresses = _own_addresses
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

        res = execute_order(order, handler)

        conn.send(res)

    conn.send(own_addresses)

    msgs_folders = None

def pEp_instance_main(iname, tmpdirname, *args):
    # run with a dispensable $HOME to get fresh DB and PGP keyrings
    print("Instance " + iname + " runs into " + tmpdirname)
    os.environ['HOME'] = tmpdirname
    pEp_instance_run(iname, *args)
    print(iname + " exiting")

def start_debug(iname, proc):
    print("#"*80 + "\n" +
                "INSTANCE "  + iname + "\n" + 
                "launching debugger attaching to process "  + 
                str(proc.pid) + "\n" +
                "#"*80 + "\n")
    # TODO : linux terminal support
    #import subprocess
    #subprocess.call(['xterm', '-e', 'lldb', '-p', str(proc.pid)])
    import appscript
    appscript.app('Terminal').do_script('lldb -p ' + str(proc.pid))
    time.sleep(2)

def start_instance(iname, tmpdir=None, instance_addresses = []):
    global handshakes_seen, handshakes_validated, msgs_folders

    if tmpdir is None:
        tmpdir = tempfile.TemporaryDirectory()

    tmpdirname = tmpdir.name
    conn, child_conn = multiprocessing.Pipe()
    proc = multiprocessing.Process(
        target=pEp_instance_main,
        args=(iname, tmpdirname, instance_addresses,
              child_conn, msgs_folders, 
              handshakes_seen, handshakes_validated))
    proc.start()

    debug = False
    if "debug_"+iname in sys.argv :
        debug = True
    if not debug and "wait_for_debug" in sys.argv :
        yes = input("#"*80 + "\n" +
                    "INSTANCE "  + iname + "\n" + 
                    "Enter y/yes/Y/YES to attach debugger to process "  + 
                    str(proc.pid) + "\nor just press ENTER\n" +
                    "#"*80 + "\n")
        if yes in ["y", "Y", "yes" "YES"]:
            debug = True
    if debug :
        start_debug(iname, proc)

    return (proc, conn, tmpdir, 0)

def get_instance(iname):
    global instances
    if iname not in instances:
        res = start_instance(iname)
        instances[iname] = res
        return res
    else:
        return instances[iname]

def stop_instance(iname):
    proc, conn, tmpdir, execnt = instances.pop(iname)
    # tell process to terminate
    conn.send(None)
    instance_addresses = conn.recv()
    proc.join()
    return tmpdir, instance_addresses

def purge_instances():
    global instances
    for iname in instances.keys():
        stop_instance(iname)

def restart_instance(iname):
    tmpdir, instance_addresses = stop_instance(iname)
    instances[iname] = start_instance(iname, tmpdir, instance_addresses)

def run_instance_action(action):
    iname, order = action
    proc, conn, tmpdir, execnt = get_instance(iname)
    execnt = execnt + 1
    instances[iname] = (proc, conn, tmpdir, execnt)
    debug_here_arg = "debug_"+iname+"_"+str(execnt)
    print(iname, ": execution number :", execnt , "(add", debug_here_arg, "to args to debug from here)")
    if debug_here_arg in sys.argv :
        start_debug(iname, proc)
    conn.send(order)
    return conn.recv()

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

        sc = scenario()
        try:
            action = next(sc)
            while True:
                res = None
                output = None
                if len(action) > 1 and type(action[-1]) == types.FunctionType:
                    output = action[-1]
                    action = action[:-1]

                if type(action[0]) == str:
                    res = run_instance_action(action)
                else:
                    res = run_manager_action(action)

                if output is not None:
                    output(res, action)

                action = sc.send(res)
        except StopIteration: pass

        if "wait_for_cleanup" in sys.argv:
            for iname,(proc, conn, tmpdir, execnt) in instances.items():
                print("Instance " + iname + " waits into " + tmpdir.name)
            input("#"*80 + "\n" +
                  "Press ENTER to cleanup\n" +
                  "#"*80 + "\n")

        purge_instances()

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
            return count

        if count >= maxcycles:
            raise Exception("Too many cycles waiting for stability") 
    
def expect(expectation):
    def _expect(res, action):
        if(expectation != res):
            raise Exception("Expected " + str(expectation) + ", got " + str(res)) 
    return _expect

