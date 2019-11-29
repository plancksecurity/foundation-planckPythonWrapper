import imaplib
import pathlib
import time
import os
from secrets import token_urlsafe

try:
    import imap_settings as settings
except:
    raise ValueError("Imap settings file not found, please check the readme")


def connect():
    "connect to the IMAP server Inbox"
    server = imaplib.IMAP4_SSL(settings.IMAP_HOST)
    server.login(settings.IMAP_USER, settings.IMAP_PWD)
    tmp, data = server.select('Inbox')

    # When you connect to the inbox one of the parameters returned is the
    # current number of messages in it
    if os.environ.get('NUMMESSAGES') is None:
        os.environ["NUMMESSAGES"] = data[0].decode("UTF-8")

    return server

def bytesmessage_to_string(msg):
    "converts bytes-like message to string"
    if type(msg) is bytes:
        msg = msg.decode("UTF-8").rstrip()
        return msg
    else:
        return str(msg)

def send(inbox, msg):
    "send msg to inbox in MIME format"

    server = connect()
    tmp, data = server.append(inbox, flags='', date_time=time.time(), message=str(msg).encode("UTF-8"))
    server.close()


def recv_all():
    """receive a list of all MIME messages from inbox newer than the last message when first connected"""

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
    tmp, data = server.search(None, 'ALL')
    for num in data[0].split():
        server.store(num, '+FLAGS', '\\Deleted')
    server.expunge()
    server.close()
    print('IMAP inbox empty.')


def backup_inbox():
    """copy all messsages from IMAP to local backup folder"""
    server = connect()
    tmp, data = server.search(None, 'ALL')
    for num in data[0].split():
        tmp, data = server.fetch(num, '(RFC822 BODY[HEADER])')
        device = str(data[0][1]).split('From: "')[1].split(' of')[0]
        name = device + "_" + token_urlsafe(16) + ".eml"
        msg = bytesmessage_to_string(data[0][1])
        with open(os.path.join('Backup/TestInbox',name), "wb") as f:
            f.write(str(msg).encode())

    server.close()

def restore_inbox():
    """copy all the messages from the Backup folder to the IMAP inbox"""
    server = connect()
    backups = pathlib.Path("./Backup/TestInbox")
    emails = backups.glob("*.eml")
    l = [ path for path in emails ]
    for p in l:
        with open(p, "rb") as f:
            tmp, data = server.append("Inbox", flags='', date_time=p.stat().st_ctime, message=f.read(-1))
    
    server.close()
