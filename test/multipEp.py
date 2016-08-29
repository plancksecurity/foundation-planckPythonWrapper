import os
import multiprocessing
import importlib
import tempfile
from collections import OrderedDict

# per-instance globals
pEp = None
handler = None
own_addresses = []
sent_messages = []

def pEp_instance_run(iname, conn):
    global pEp, handler, sent_messages

    pEp = importlib.import_module("pEp")

    hdr = "-" * (39 - int(len(iname)/2))  + " " + iname + " " + "-" * (39 - len(iname) + int(len(iname)/2))

    class Handler(pEp.SyncMixIn):
        def messageToSend(self, msg):
            msgstr = str(msg)
            print(hdr)
            print(msgstr.replace("\r", ""))
            print("-" * 80)
            sent_messages.append(msgstr)

        def showHandshake(self, me, partner):
            print(hdr)
            print("handshake needed between " + repr(me) + " and " + repr(partner))
            print("-" * 80)
            # TODO: accept or reject

    handler = Handler()

    while True:
        order = conn.recv()
        if order is None:
            break

        command, new_msgs = order

        if new_msgs is not None:
            for msgstr in new_msgs:
                msg = pEp.incoming_message(msgstr)
                for to in msg.to:
                    # check if mail is for an account owned by that instance
                    # checking if to.user_id == pEp.PEP_OWN_USERID
                    # could lead to false positive depending on what pEpEngine
                    # consider to be its own identity
                    if to.address in own_addresses:
                        decrypt_result = msg.decrypt()
                        break

        res = None
        if command is not None:
            func = command[0]
            args, kwargs = command[1:] + [[], {}][len(command) - 1:]
            print(func, args, kwargs)
            res = func(*args,**kwargs)
            print(func, args, kwargs, " -> ", res)

        conn.send([res, sent_messages])
        sent_messages = []

def pEp_instance_main(iname, conn):
    # run with a dispensable $HOME to get fresh DB and PGP keyrings
    with tempfile.TemporaryDirectory() as tmpdirname:
        print(iname + " instance runs into " + tmpdirname)
        os.environ['HOME'] = tmpdirname
        pEp_instance_run(iname, conn)
        print(iname + " exiting")

def run_scenario(scenario):
    instances = OrderedDict()
    for iname, order in scenario:
        if iname not in instances:
            to_inst_msg = []
            conn, child_conn = multiprocessing.Pipe()
            proc = multiprocessing.Process(target=pEp_instance_main, args=(iname,child_conn))
            proc.start()
            instances[iname] = (proc, conn, to_inst_msg)
        else:
            proc, conn, to_inst_msg = instances[iname]

        conn.send([order, to_inst_msg])
        res, from_inst_msgs = conn.recv()

    for iname, (proc, conn, to_inst_msg) in instances.items():
        # tell process to terminate
        conn.send(None)
        proc.join()

