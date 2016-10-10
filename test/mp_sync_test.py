"""
test for simplest keysync scenario : two device setting up same account

Launch it with something like :
LC_ALL=en_US.UTF-8 \
DYLD_LIBRARY_PATH=/Users/ed/lib/ \
PYTHONPATH=`pwd`/../build/lib.macosx-10.11-x86_64-3.4 \
python3.4 mp_sync_test.py

"""

stored_message = []

def store_message(res, action):
    stored_message.append(res)

def print_res(res, action):
    print(res)

from multipEp import *

   #("instance name", [instance_action_func, [args], {kwargs}], result_func),
   #(manager_action_func, [args], {kwargs}, result_func),
scenario0 = [
    ("GroupA1", [create_account, ["some.one@some.where", "Some One"]]),
    ("SoloA", [create_account, ["some.other@else.where", "Some Other"]]),
    # key exchange
    ("SoloA", [send_message, ["some.other@else.where", "some.one@some.where", 
                              "Hey Bro", "Heeeey Brooooo"]]),
    ("GroupA1", [send_message, ["some.one@some.where", "some.other@else.where",
                                "Yo Dude", "Yooooo Duuuude"]]),
    ("SoloA", [encrypted_message, ["some.other@else.where", 
                                   "some.one@some.where", 
                                   "read this", "this is a secret message"]], store_message),
    (flush_all_mails,),
    ("GroupA2", [create_account, ["some.one@some.where", "Some One"]]),
    (cycle_until_no_change, ["GroupA1", "GroupA2"], expect(4)),
    ("GroupA2", [decrypt_message, [stored_message]], print_res), 
    ("GroupA3", [create_account, ["some.one@some.where", "Some One"]]),
    (cycle_until_no_change, ["GroupA1", "GroupA2", "GroupA3"], expect(3)),
    # force consume messages
    ("GroupA3", [None, None, None, -60*15])
] 

scenario1 = [
   #("instance name", [func, [args], {kwargs}]),
    ("B", [send_message, ["some.other@else.where", "some.one@some.where", "Hey Bro", "Heeeey Brooooo"]]),
    ("A", [send_message, ["some.one@some.where", "some.other@else.where", "Hey Bro", "Heeeey Brooooo"]]),
] 

if __name__ == "__main__":
    run_scenario(scenario0)

