"""
test for simplest keysync scenario : two device setting up same account

Launch it with something like :
LC_ALL=en_US.UTF-8 \
DYLD_LIBRARY_PATH=/Users/ed/lib/ \
PYTHONPATH=`pwd`/../build/lib.macosx-10.11-x86_64-3.4 \
python3.4 mp_sync_test.py

"""

from multipEp import *

#("instance name", [instance_action_func, [args], {kwargs}], result_func),
#(manager_action_func, [args], {kwargs}, result_func),

def group_on_keygen():
    for action in [
        ("GroupA1", [create_account, ["some.one@some.where", "Some One"]]),
        ("SoloA", [create_account, ["some.other@else.where", "Some Other"]]),
        # key exchange
        ("SoloA", [send_message, ["some.other@else.where",
                                  "some.one@some.where", 
                                  "Hey Bro", "Heeeey Brooooo"]]),
        ("GroupA1", [send_message, ["some.one@some.where",
                                    "some.other@else.where",
                                    "Yo Dude", "Yooooo Duuuude"]])
    ] : yield action

    enc_msg = yield ("SoloA", [encrypted_message, ["some.other@else.where", 
                                   "some.one@some.where", 
                                   "read this", "this is a secret message"]])
    for action in [
        ("GroupA1", [decrypt_message, [enc_msg]], expect(PEP_rating_reliable)),
        (flush_all_mails,),
        ("GroupA2", [create_account, ["some.one@some.where", "Some One"]]),
        (cycle_until_no_change, ["GroupA1", "GroupA2"], expect(4)),
        ("GroupA2", [decrypt_message, [enc_msg]], expect(PEP_rating_reliable)) 
    ] : yield action

    return enc_msg

def group_on_cannotdecypt():
    for action in [
        ("GroupA1", [create_account, ["some.one@some.where", "Some One"]]),
        ("SoloA", [create_account, ["some.other@else.where", "Some Other"]]),
        # key exchange
        ("SoloA", [send_message, ["some.other@else.where",
                                  "some.one@some.where", 
                                  "Hey Bro", "Heeeey Brooooo"]]),
        ("GroupA1", [send_message, ["some.one@some.where",
                                    "some.other@else.where",
                                    "Yo Dude", "Yooooo Duuuude"]])
    ] : yield action

    enc_msg = yield ("SoloA", [encrypted_message, ["some.other@else.where", 
                                   "some.one@some.where", 
                                   "read this", "this is a secret message"]])
    for action in [
        ("GroupA1", [decrypt_message, [enc_msg]], expect(PEP_rating_reliable)),
        (flush_all_mails,),
        ("GroupA2", [create_account, ["some.one@some.where", "Some One"]]),
        (flush_all_mails,),
        ("GroupA2", [decrypt_message, [enc_msg]], expect(PEP_rating_have_no_key)),
        (cycle_until_no_change, ["GroupA1", "GroupA2"], expect(4)),
        ("GroupA2", [decrypt_message, [enc_msg]], expect(PEP_rating_reliable)),
    ] : yield action

def group_of_3_members():
    enc_msg = yield from group_on_keygen()
    for action in [
        ("GroupA3", [create_account, ["some.one@some.where", "Some One"]]),
        (cycle_until_no_change, ["GroupA1", "GroupA2", "GroupA3"], expect(3)),
        # force consume messages
        # ("GroupA3", [None, None, None, -60*15]),
        ("GroupA3", [decrypt_message, [enc_msg]], expect(PEP_rating_reliable)) 
    ] : yield action

    return enc_msg

if __name__ == "__main__":
    run_scenario(group_on_keygen)
    run_scenario(group_on_cannotdecypt)
    run_scenario(group_of_3_members)

