= Tests in this directory =

$ HOME=$PWD python3 basic_doctest.py -v
    do some basic tests of p≡p

    CAVEAT: set environment variable HOME to a test directory before executing
    this test

$ python3 sync_test.py
    start two processes representing two devices and do a sync test

Once started sync_handshake.py is creating a trace of all sent messages in
TestInbox. There's a file named Laptop or Phone, respectively, which is working
as a marker; the modification timestamp of this file is showing the mails being
considered as “already received”. If you delete the file and start i.e.

$ cd Phone
$ rm ../TestInbox/Phone
$ HOME=$PWD lldb python3 --  ../sync_handshake.py -e Phone

Then this side is doing a replay in the debugger.  Using touch to set a
different timestamp on the marker will only partly replay.

In order to work with IMAP you need to create a imap_settings.py file with the
following variables:

IMAP_HOST = 'domain.ch'
IMAP_PORT = '993'
IMAP_USER = 'your_username'
IMAP_PWD = 'password'
IMAP_EMAIL = 'user@domain.ch'

= Hint =

installing termcolor and lxml will beautify the output

