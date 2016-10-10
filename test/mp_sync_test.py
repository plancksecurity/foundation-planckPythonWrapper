"""
test for simplest keysync scenario : two device setting up same account

Launch it with something like :
DYLD_LIBRARY_PATH=/Users/ed/lib/ PYTHONPATH=`pwd`/../build/lib.macosx-10.11-x86_64-3.4 python3.4 sync_test.py

"""

import multipEp as mp


scenario0 = [
   #("instance name", [func, [args], {kwargs}]),
    ("A", [mp.create_account, ["some.one@some.where", "Some One"]]),
    ("B", [mp.create_account, ["some.one@some.where", "Some One"]]),
    (mp.cycle_until_no_change, ["A", "B"]),
    ("C", [mp.create_account, ["some.one@some.where", "Some One"]]),
    (mp.cycle_until_no_change, ["A", "B", "C"]),
    # force consume messages
    ("C", [None, None, None, -60*15])
] 

scenario1 = [
   #("instance name", [func, [args], {kwargs}]),
    ("A", [mp.send_message, ["some.one@some.where", "some.other@else.where", "Hey Bro", "Heeeey Brooooo"]]),
    ("B", [mp.send_message, ["some.other@else.where", "some.one@some.where", "Hey Bro", "Heeeey Brooooo"]]),
] 

if __name__ == "__main__":
    mp.run_scenario(scenario0)

