import imaplib
import pprint
import email.message
import email.charset
import time
import os
import imap_settings as settings


def connect():
    "connect to the IMAP server Inbox"
    server = imaplib.IMAP4_SSL(settings.IMAP_HOST)
    server.login(settings.IMAP_USER, settings.IMAP_PWD)
    tmp, data = server.select('Inbox')
    if os.environ.get('NUMMESSAGES') is None:
        os.environ["NUMMESSAGES"] = data[0].decode("UTF-8")

    return server

def bytesmessage_to_string(msg):
    "converts bytes-like message to string"
    msg = msg.decode("UTF-8").rstrip()
    return msg

def send(inbox, msg):
    "send msg to inbox in MIME format"
    print("send imap")

    server = connect()
    tmp, data = server.append('Inbox', '', imaplib.Time2Internaldate(time.time()), str(msg).encode("UTF-8"))
    server.close()


def recv_all(inbox):
    """receive a list of all MIME messages from inbox newer than the last message when first connected"""
    print("recieve imap")

    server = connect()
    r = []

    tmp, data = server.search(None, 'ALL')

    oldermsgid = os.environ.get('NUMMESSAGES')

    for num in data[0].split():
        if int(num) >= int(oldermsgid):
            tmp, data = server.fetch(num, '(RFC822)')
            msg = bytesmessage_to_string(data[0][1])
            r.append((num, msg))
            os.environ["NUMMESSAGES"] = num.decode("UTF-8")

    server.close()

    return r


def clean_inbox():
    """clean all messsages from IMAP inbox"""
    print('cleaning IMAP...')
    server = connect()
    typ, data = server.search(None, 'ALL')
    for num in data[0].split():
        server.store(num, '+FLAGS', '\\Deleted')
    server.expunge()
    server.close()
    print('IMAP inbox empty.')


