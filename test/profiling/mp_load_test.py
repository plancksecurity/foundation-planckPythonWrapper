"""
load tests

Launch it with something like :
LC_ALL=en_US.UTF-8 \
DYLD_LIBRARY_PATH=/Users/ed/lib/ \
PYTHONPATH=`pwd`/../build/lib.macosx-10.11-x86_64-3.4 \
python3.4 mp_load_test.py

"""

import multipEp
from multipEp import *
from os import system, path, environ
from shutil import copyfile
curpath = path.dirname(path.abspath(__file__))

#("instance name", [instance_action_func, [args], {kwargs}], result_func),
#(manager_action_func, [args], {kwargs}, result_func),

multipEp.disable_sync = True

def import_5k_keys():
    copyfile(path.join(curpath, "5k_pubring.gpg"),
             path.join(environ["HOME"], ".gnupg", "pubring.gpg") )

def handshake_with_heavy_ring():
    for action in [
        ("Alice", [import_5k_keys]),
        #("Bob", [import_5k_keys]),
        (restart_instance, ["Alice"]),
        #(restart_instance, ["Bob"]),
        ("Alice", [create_account, ["mail@alice.a", "Alice mail"]]),
        ("Bob", [create_account, ["mail@bob.a", "mail Bob"]]),
        (flush_all_mails,),
        # key exchange
        ("Bob", [send_message, ["mail@bob.a",
                                  "mail@alice.a",
                                  "Bob mail to Alice mail",
                                  "Bob mail to Alice mail -- long"]]),
        ("Alice", [send_message, ["mail@alice.a",
                                    ["mail@bob.a",
                                     "test1@peptest.ch",
                                     "test2@peptest.ch",
                                     "test3@peptest.ch",
                                     "test4@peptest.ch",
                                     "test5@peptest.ch",
                                     "test6@peptest.ch",
                                     "test7@peptest.ch",
                                     "test8@peptest.ch",
                                     "test9@peptest.ch",
                                     "test10@peptest.ch"
                                     ],
                                    "Alice mail to Bob mail",
                                    "Alice mail to Bob mail -- long"]])
    ] : yield action
    # enc_msg = yield ("Bob", [encrypted_message, ["mail@bob.a", 
    #                          "mail@alice.a", 
    #                          "Bob mail to Alice mail -- encrypted",
    #                          "Bob mail to Alice mail -- long encrypted"]])
    # for action in [
    #     ("Alice", [decrypt_message, [enc_msg]], expect(pEp.PEP_rating.PEP_rating_reliable))
    # ] : yield action


if __name__ == "__main__":
    run_scenario(handshake_with_heavy_ring)

