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

def pre_existing_peers_with_encrypted_mail():
    for action in [
        ("GroupA1", [create_account, ["first@group.a", "GroupA First"]]),
        ("SoloA", [create_account, ["first@solo.a", "First SoloA"]]),
        # key exchange
        ("SoloA", [send_message, ["first@solo.a",
                                  "first@group.a", 
                                  "SoloA First to GroupA First",
                                  "SoloA First to GroupA First -- long"]]),
        ("GroupA1", [send_message, ["first@group.a",
                                    "first@solo.a",
                                    "GroupA First to SoloA First",
                                    "GroupA First to SoloA First -- long"]])
    ] : yield action

    enc_msg = yield ("SoloA", [encrypted_message, ["first@solo.a", 
                             "first@group.a", 
                             "SoloA First to GroupA First -- encrypted",
                             "SoloA First to GroupA First -- long encrypted"]])
    for action in [
        ("GroupA1", [decrypt_message, [enc_msg]], expect(PEP_rating_reliable)),
        (flush_all_mails,),
    ] : yield action

    return enc_msg

def group_on_keygen():
    enc_msg = yield from pre_existing_peers_with_encrypted_mail()
    for action in [
        ("GroupA2", [create_account, ["first@group.a", "GroupA First"]]),
        (cycle_until_no_change, ["GroupA1", "GroupA2"], expect(4)),
        ("GroupA2", [decrypt_message, [enc_msg]], expect(PEP_rating_reliable)) 
    ] : yield action

    return enc_msg

def group_on_cannotdecrypt():
    enc_msg = yield from pre_existing_peers_with_encrypted_mail()
    for action in [
        ("GroupA2", [create_account, ["first@group.a", "GroupA First"]]),
        (flush_all_mails,),
        ("GroupA2", [decrypt_message, [enc_msg]], expect(PEP_rating_have_no_key)),
        (cycle_until_no_change, ["GroupA1", "GroupA2"], expect(4)),
        ("GroupA2", [decrypt_message, [enc_msg]], expect(PEP_rating_reliable)),
    ] : yield action

def group_of_3_members():
    enc_msg = yield from group_on_keygen()
    for action in [
        ("GroupA3", [create_account, ["first@group.a", "GroupA First"]]),
        (cycle_until_no_change, ["GroupA1", "GroupA2", "GroupA3"], expect(4)),
        # force consume messages
        # ("GroupA3", [None, None, None, -60*15]),
        ("GroupA3", [decrypt_message, [enc_msg]], expect(PEP_rating_reliable)) 
    ] : yield action

    return enc_msg

def keygen_in_a_group_of_3_members():
    prev_enc_msg = yield from group_of_3_members()
    for action in [
        ("SoloB", [create_account, ["first@solo.b", "First SoloB"]]),
        ("GroupA3", [create_account, ["second@group.a", "GroupA Second"]]),
        # key exchange
        ("SoloB", [send_message, ["first@solo.b",
                                  "second@group.a", 
                                  "SoloB First to GroupA second",
                                  "SoloB First to GroupA second -- long"]]),
        ("GroupA3", [send_message, ["second@group.a",
                                    "first@solo.b",
                                    "GroupA second to SoloB First",
                                    "GroupA second to SoloB First"]]),
    ] : yield action

    enc_msg = yield ("SoloB", [encrypted_message, ["first@solo.b", 
                             "second@group.a", 
                             "SoloB First to GroupA Second -- encrypted",
                             "SoloB First to GroupA Second -- long encrypted"]])
    for action in [
        (cycle_until_no_change, ["GroupA1", "GroupA2", "GroupA3"], expect(1)),
        ("GroupA1", [create_account, ["second@group.a", "GroupA Second"]]),
        ("GroupA2", [create_account, ["second@group.a", "GroupA Second"]]),
        ("GroupA2", [decrypt_message, [enc_msg]], expect(PEP_rating_reliable)),
        ("GroupA1", [decrypt_message, [enc_msg]], expect(PEP_rating_reliable)),
    ] : yield action

def nokey_in_a_group_of_3_members():
    prev_enc_msg = yield from group_of_3_members()
    for action in [
        ("SoloB", [create_account, ["first@solo.b", "First SoloB"]]),
        ("GroupA3", [create_account, ["second@group.a", "GroupA Second"]]),
        # key exchange
        ("SoloB", [send_message, ["first@solo.b",
                                  "second@group.a", 
                                  "SoloB First to GroupA second",
                                  "SoloB First to GroupA second -- long"]]),
        ("GroupA3", [send_message, ["second@group.a",
                                    "first@solo.b",
                                    "GroupA second to SoloB First",
                                    "GroupA second to SoloB First"]]),
    ] : yield action

    enc_msg = yield ("SoloB", [encrypted_message, ["first@solo.b", 
                             "second@group.a", 
                             "SoloB First to GroupA Second -- encrypted",
                             "SoloB First to GroupA Second -- long encrypted"]])
    for action in [
        (flush_all_mails,),
        ("GroupA1", [create_account, ["second@group.a", "GroupA Second"]]),
        (flush_all_mails,),
        ("GroupA1", [decrypt_message, [enc_msg]], expect(PEP_rating_have_no_key)),
        (cycle_until_no_change, ["GroupA1", "GroupA2", "GroupA3"], expect(3)),
        ("GroupA1", [decrypt_message, [enc_msg]], expect(PEP_rating_reliable)),
        ("GroupA2", [create_account, ["second@group.a", "GroupA Second"]]),
        ("GroupA2", [decrypt_message, [enc_msg]], expect(PEP_rating_reliable)),
    ] : yield action

if __name__ == "__main__":
    run_scenario(group_on_keygen)
    run_scenario(group_on_cannotdecrypt)
    run_scenario(group_of_3_members)
    run_scenario(keygen_in_a_group_of_3_members)
    run_scenario(nokey_in_a_group_of_3_members)

