"""
test for simplest keysync scenario : two device setting up same account

Launch it with something like :
DYLD_LIBRARY_PATH=/Users/ed/lib/ PYTHONPATH=`pwd`/../build/lib.macosx-10.11-x86_64-3.4 python3.4 sync_test.py

"""

import multipEp as mp

# unused
def send_message(from_address, to_address):
    m = mp.pEp.outgoing_message(Identity(from_address, from_address))
    m.to = [mp.pEp.Identity(to_address, to_address)]
    m.shortmsg = "Hello"
    m.longmsg = "Something\\n"
    m.encrypt()
    mp.sent_messages.append(str(m))

scenario0 = [
   #("instance name", ["func name", [args], {kwargs}]),
    ("A", [mp.create_account, ["some.one@some.where", "Some One"]]),
    ("B", [mp.create_account, ["some.one@some.where", "Some One"]]),
    ("A", []),
    ("B", []),
    ("A", []),
    ("B", []),
    ("A", []),
    ("B", []),
    ("C", [mp.create_account, ["some.one@some.where", "Some One"]]),
    ("A", []),
    ("B", []),
    ("C", []),
    ("A", []),
    ("B", []),
    ("C", []),
    ("A", []),
    ("B", []),
    ("C", []),
    ("A", []),
    ("B", []),
    ("C", []),
    ("A", []),
    ("B", []),
    ("C", [None, None, None, -60*15])
] 

if __name__ == "__main__":
    mp.run_scenario(scenario0)

