import os
import multiprocessing
import importlib
import tempfile
from collections import OrderedDict

# per-instance globals
pEp = None
handler = None
own_addresses = []

def create_account(address, name):
    global own_addresses
    i = pEp.Identity(address, name)
    pEp.myself(i)
    own_addresses.append(address)

def header(blah=None):
    if blah is None:
        return "-" * 80
    else:
        return ("-" * (39 - int(len(blah)/2))  + 
                " " + blah + " " + 
                "-" * (39 - len(blah) + int(len(blah)/2)))


def pEp_instance_run(iname, conn, msgs_folders):
    global pEp, handler, own_addresses 

    pEp = importlib.import_module("pEp")

    class Handler(pEp.SyncMixIn):
        def messageToSend(self, msg):
            print(header("SYNC MESSAGE from instance"+iname))
            print("from :", msg.from_)
            print("to :", msg.to)
            print("short :", msg.shortmsg)
            print("long :", (msg.longmsg[:250]+" [...]"
                             if len(msg.longmsg)>250 
                             else msg.longmsg))
            print(msg.attachments)
            print(header())
            for rcpt in msg.to + msg.cc + msg.bcc:
                # list inside dict from MP manager are not mutable, apparently.
                msgs = msgs_folders.get(rcpt.address,[])
                msgs.append(str(msg))
                msgs_folders[rcpt.address] = msgs

        def showHandshake(self, me, partner):
            print(header("HANDSHAKE from instance"+iname))
            print("handshake needed between " + repr(me) + " and " + repr(partner))
            print(header())
            # TODO: accept or reject

    handler = Handler()

    while True:
        order = conn.recv()
        if order is None:
            break

        func = order[0]

        print(header("DECRYPT messages for instance "+iname))
        # decrypt every non-consumed message for all instance accounts
        for own_address in own_addresses:
            msgs_for_me = msgs_folders[own_address]
            for idx, msgstr in enumerate(msgs_for_me):
                msg = pEp.incoming_message(msgstr)
                decrypt_result = msg.decrypt()
                # TODO get status instead of an exception when consumed...
                #if decrypt_result == 0xff02: #PEP_MESSAGE_CONSUMED
                #    msgs_for_me.pop(idx)
        print(header())

        res = None
        if func is not None:
            print(header("Instance " + iname + " : function " + func.__name__))
            args, kwargs = order[1:] + [[], {}][len(order) - 1:]
            print("args :", args)
            print("kwargs :", kwargs)
            res = func(*args,**kwargs)
            print(" -> ", res)
            print(header())

        conn.send(res)

def pEp_instance_main(iname, conn, msgs_folders):
    # run with a dispensable $HOME to get fresh DB and PGP keyrings
    with tempfile.TemporaryDirectory() as tmpdirname:
        print("Instance " + iname + " runs into " + tmpdirname)
        os.environ['HOME'] = tmpdirname
        pEp_instance_run(iname, conn, msgs_folders)
        print(iname + " exiting")

def run_scenario(scenario):
    instances = OrderedDict()
    with multiprocessing.Manager() as manager:
        msgs_folders = manager.dict()
        for iname, order in scenario:
            if iname not in instances:
                conn, child_conn = multiprocessing.Pipe()
                proc = multiprocessing.Process(
                    target=pEp_instance_main,
                    args=(iname,child_conn,msgs_folders))
                proc.start()
                instances[iname] = (proc, conn)
            else:
                proc, conn = instances[iname]

            conn.send(order)
            res = conn.recv()

        for iname, (proc, conn) in instances.items():
            # tell process to terminate
            conn.send(None)
            proc.join()

