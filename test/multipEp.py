"""
  multipEp.py : multiple process python testing framework for pEp

  = Command line switches =

  wait_for_debug
    Block and ask if debugger should be attached each time an instance
    is started

  debug_${instance_name}
    Launch lldb in another terminal, and attach it to given intsance
    immediately after instance startup.

  debug_${instance_name}_${execution_number}
    Launch lldb in another terminal, and attach it to given intsance
    when instance is at some particular step in the test.
    ${execution_number} is found by reading test output.

  only_${test_scenario_name}
    Execute only given test scenario. Scenario with different name
    are skipped.

  libs_${instance_name}=/path/to/libs
    Set LD_LIBRARY_PATH to given path before launching instance,
    meant to allow selection of per-instance pEpEngines flavors

  wait_for_cleanup
    Block at the end of each test scenario, before deleting temporary
    directory. It is meant to be able to examine keyring and DBs after
    test finished or crashed.

"""

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

# ----------------------------------------------------------------------------
#                                  GLOBALS
# ----------------------------------------------------------------------------

# per-instance globals
sync_handler = None
own_addresses = []
indent = 0
i_name = ""
handshakes_pending = None
pEp = None

# manager globals
instances = None
if(multiprocessing.current_process().name == "MainProcess"):
    ctx = multiprocessing.get_context('spawn')
    # import pEp in main process to get enums
    pEp = importlib.import_module("pEp")

# both side globals (managed by MP)
handshakes_seen = None
test_config = None
msgs_folders = None

# both side globals (not managed)
disable_sync = False

# ----------------------------------------------------------------------------
#                               INSTANCE ACTIONS
# ----------------------------------------------------------------------------

def create_account(address, name, flags=None):
    global own_addresses
    i = pEp.Identity(address, name)
    if flags is not None:
        i.flags = flags
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
    m = pEp.outgoing_message(pEp.Identity(from_address, from_address))
    if type(to_address) != list :
        to_address = [to_address]
    m.to = [ pEp.Identity(address, address) for address in to_address ]
    m.shortmsg = shortmsg
    m.longmsg = longmsg
    begin = time.time()
    ret = m.encrypt()
    end = time.time()
    printi("ENCRYPTION TIME:", end - begin)
    return ret

def encrypted_message(from_address, to_address, shortmsg, longmsg):
    return str(_encrypted_message(from_address, to_address, shortmsg, longmsg))

def send_message(from_address, to_address, shortmsg, longmsg):
    msg = _encrypted_message(from_address, to_address, shortmsg, longmsg)
    if type(to_address) != list :
        to_address = [to_address]
    for address in to_address:
        _send_message(address, msg)

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

def simulate_timeout():
    global sync_handler
    sync_handler.onTimeout()

no_inbox_decrypt = [simulate_timeout, create_account]
# ----------------------------------------------------------------------------
#                               MANAGER ACTIONS
# ----------------------------------------------------------------------------

def flush_all_mails():
    global msgs_folders
    count = sum(map(len,msgs_folders.values()))
    msgs_folders.clear()
    return count

def restart_instance(iname):
    tmpdir, instance_addresses = stop_instance(iname)
    instances[iname] = start_instance(iname, tmpdir, instance_addresses)

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

def disable_auto_handshake():
    global test_config
    test_config.disable_handshake = True

def enable_auto_handshake():
    global test_config
    test_config.disable_handshake = False

def expect(expectation):
    def _expect(res, action):
        if(expectation != res):
            raise Exception("Expected " + str(expectation) + ", got " + str(res)) 
    return _expect

# ----------------------------------------------------------------------------
#                               "PRETTY" PRINTING
# ----------------------------------------------------------------------------

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
    printi("from :", repr(msg.from_))
    printi("to :", repr(msg.to))
    printi("recv :", msg.recv)
    printi("sent :", msg.sent)
    printi("short :", msg.shortmsg)
    printi("opt_fields :", msg.opt_fields)
    lng = msg.longmsg.splitlines()
    lngcut = lng[:40]+["[...]"] if len(lng)>40 else lng
    pfx = "long : "
    for l in lngcut :
        printi(pfx + l)
        pfx = "       "
    printi("attachments : ", msg.attachments)

# ----------------------------------------------------------------------------
#                          INSTANCE TEST EXECUTION
# ----------------------------------------------------------------------------

def execute_order(order):
    global handshakes_pending, hanshakes_seen
    global test_config, msgs_folders, own_addresses, sync_handler

    func, args, kwargs, timeoff = order[0:] + [None, [], {}, 0][len(order):]

    printheader("DECRYPT messages")
    # decrypt every non-consumed message for all instance accounts
    if func not in no_inbox_decrypt :
        for own_address in own_addresses :
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

    res = None
    if func is not None:
        printheader("Executing instance function " + func.__name__)
        printi("args :", args)
        printi("kwargs :", kwargs)
        res = func(*args,**kwargs)
        printi("function " + func.__name__ + " returned :", res)
        printheader()

    if handshakes_pending and not test_config.disable_handshake :
        printheader("check pending handshakes accepted on other device")
        tw, partner, nth_seen = handshakes_pending
        if handshakes_seen[tw] >= test_config.handshake_count_to_accept :
            if nth_seen in [1, test_config.handshake_count_to_accept]:
                # equiv to close dialog 
                handshakes_pending = None
                printi("ACCEPT pending handshake : "+ tw)
                sync_handler.deliverHandshakeResult(partner, 0)
                # else dialog closed later by OVERTAKEN notification
        printheader()

    return res

def pEp_instance_run(iname, _own_addresses, conn, _msgs_folders, _handshakes_seen, _test_config):
    global pEp, sync_handler, own_addresses, i_name, msgs_folders
    global handshakes_pending
    global handshakes_seen, test_config

    # assign instance globals
    own_addresses = _own_addresses
    msgs_folders = _msgs_folders
    handshakes_seen = _handshakes_seen
    test_config = _test_config
    i_name = iname

    pEp = importlib.import_module("pEp")

    class Handler(pEp.SyncMixIn):
        def messageToSend(self, msg):
            printheader("SYNC MESSAGE to send")
            printmsg(msg)
            printheader()
            for rcpt in msg.to + msg.cc + msg.bcc:
                _send_message(rcpt.address, msg)

        def notifyHandshake(self, me, partner, signal):
            global handshakes_pending
            if test_config.disable_handshake :
                printheader("HANDSHAKE disabled. Notification ignored")
                printi(signal)
                printheader()
                return

            if signal in [
                 pEp.sync_handshake_signal.SYNC_NOTIFY_INIT_ADD_OUR_DEVICE,
                 pEp.sync_handshake_signal.SYNC_NOTIFY_INIT_ADD_OTHER_DEVICE,
                 pEp.sync_handshake_signal.SYNC_NOTIFY_INIT_FORM_GROUP,
                 pEp.sync_handshake_signal.SYNC_NOTIFY_INIT_MOVE_OUR_DEVICE]:
                printheader("show HANDSHAKE dialog")
                printi(signal)
                printi("handshake needed between " + repr(me) + " and " + repr(partner))
                tw = pEp.trustwords(me, partner, 'en', True)
                printi(tw)

                # This is an error from pEpEngine if asked to open handshake dialog twice
                if handshakes_pending:
                    raise Exception("Asked to open a second Sync Handshake Dialog !") 

                if tw in handshakes_seen :
                    handshakes_seen[tw] += 1
                else:
                    handshakes_seen[tw] = 1

                handshakes_pending = (tw,partner,handshakes_seen[tw])
                printheader()

            elif signal == pEp.sync_handshake_signal.SYNC_NOTIFY_OVERTAKEN:
                if handshakes_pending:
                    tw, partner, nth_seen = handshakes_pending
                    printi("OVERTAKEN handshake : "+ tw)
                    handshakes_pending = None
                else:
                    raise Exception("Asked to close a non existing Sync Handshake Dialog !") 
            else :
                printheader("other HANDSHAKE notification - ignored")
                printi(signal)
                printheader()

        def setTimeout(self, timeout):
           printi("SET TIMEOUT :", timeout) 

        def cancelTimeout(self):
           printi("CANCEL TIMEOUT") 
           return 42

    if not disable_sync:
        sync_handler = Handler()

    while True:
        order = conn.recv()
        if order is None:
            break

        res = execute_order(order)

        conn.send(res)

    conn.send(own_addresses)

    msgs_folders = None

def pEp_instance_main(iname, tmpdirname, *args):
    # run with a dispensable $HOME to get fresh DB and PGP keyrings
    print("Instance " + iname + " runs into " + tmpdirname)
    os.environ['HOME'] = tmpdirname

    pEp_instance_run(iname, *args)
    print(iname + " exiting")

# ----------------------------------------------------------------------------
#                          MANAGER TEST EXECUTION
# ----------------------------------------------------------------------------

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
    global handshakes_seen, test_config, msgs_folders

    given_libs = None
    for a in sys.argv:
        if a.startswith("libs_"+iname+"="):
            given_libs = a.split("=")[1]
            break

    if tmpdir is None:
        tmpdir = tempfile.TemporaryDirectory()
        if given_libs is not None:
            os.symlink(given_libs, os.path.join(tmpdir.name, "libs"))

    if sys.platform.startswith('darwin'):
        ld_env_name = 'DYLD_LIBRARY_PATH'
    else:
        ld_env_name = 'LD_LIBRARY_PATH' 

    orig_ld_env_val = None
    if given_libs is not None:
        orig_ld_env_val = os.environ.pop(ld_env_name, None)
        os.environ[ld_env_name] = os.path.join(tmpdir.name, "libs")

    conn, child_conn = ctx.Pipe()
    proc = ctx.Process(
        target=pEp_instance_main,
        args=(iname, tmpdir.name, instance_addresses,
              child_conn, msgs_folders, 
              handshakes_seen, test_config))
    proc.start()

    if orig_ld_env_val is not None:
        os.environ[ld_env_name] = orig_ld_env_val
    elif given_libs is not None:
        os.environ.pop(ld_env_name)

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
    for iname in list(instances.keys()):
        stop_instance(iname)

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
    print("------------------------- Executing manager function -----------------------------")
    print("function name :", func.__name__)
    print("args :", args)
    print("kwargs :", kwargs)
    res = func(*args, **kwargs)
    print("manager function " + func.__name__ + " returned :", res)
    print("-" * 80)
    return res

def run_scenario(scenario):
    global pEp

    for a in sys.argv:
        if a.startswith("only_") and a != "only_" + scenario.__name__ :
            print("IGNORING: " + scenario.__name__)
            return
    print("RUNNING: " + scenario.__name__)

    global handshakes_seen, test_config, msgs_folders, instances
    instances = OrderedDict()
    with ctx.Manager() as manager:
        msgs_folders = manager.dict()
        handshakes_seen = manager.dict()
        test_config = manager.Namespace(
            disable_handshake=False,
            handshake_count_to_accept=2)

        sc = scenario()
        t = None
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
        except StopIteration: 
            pass
        except : 
            t,v,tv = sys.exc_info()
            import traceback
            print("EXCEPTION IN: " + scenario.__name__)
            traceback.print_exc()

        if "wait_for_cleanup" in sys.argv:
            for iname,(proc, conn, tmpdir, execnt) in instances.items():
                print("Instance " + iname + " waits into " + tmpdir.name)
            input("#"*80 + "\n" +
                  "Press ENTER to cleanup\n" +
                  "#"*80 + "\n")

        purge_instances()

        if t: 
            raise t(v).with_traceback(tv)

