import imaplib
import pprint
import email.message
import email.charset
import time
import sync_settings as settings


def connect():
    "connect to the IMAP server Inbox"
    server = imaplib.IMAP4_SSL(settings.IMAP_HOST)
    server.login(settings.IMAP_USER, settings.IMAP_PWD)
    server.select('Inbox')

    return server

def pEpMessage_to_imap(msg):
    "convert pEpMessage to python imap formatted string"
    new_message = email.message.Message()
    new_message["From"] = str(msg.from_).replace("\n", " ")
    new_message["To"] = str(msg.to[0])
    new_message["Subject"] = msg.shortmsg
    if msg.opt_fields:
        for field, value in msg.opt_fields.items():
            new_message[field] = str(value).replace("\n", " ")
    new_message.set_payload(msg.longmsg)

    new_message.set_charset(email.charset.Charset("utf-8"))
    encoded_message = str(new_message).encode("utf-8")

    return encoded_message

def bytesmessage_to_string(msg):
    "converts bytes-like message to string"
    msg = msg.decode("UTF-8").rstrip()
    return msg

def send(inbox, msg):
    "send msg to inbox in MIME format"
    server = connect()
    msg = pEpMessage_to_imap(msg)
    print('******** sent msg *******')
    print(msg)
    server.append('Inbox', '', imaplib.Time2Internaldate(time.time()), msg)
    server.close()


def recv_all(inbox, start_time):
    """receive a list of new MIME messages from inbox, which are newer than the
    start_time"""

    server = connect()
    r = []

    tmp, data = server.search(None, 'ALL')
    # tmp, data = server.search(None, 'SENTSINCE {0}'.format(start_time.strftime("%d-%b-%Y %H:%M%S")))

    for num in data[0].split():
        tmp, data = server.fetch(num, '(RFC822)')
        msg = bytesmessage_to_string(data[0][1])
        r.append((num, msg))
        print('******** recieved msg *******')
        print(msg)

    server.close()

    return r


def clean_inbox():
    print('clean IMAP')
    server = connect()
    typ, data = server.search(None, 'ALL')
    for num in data[0].split():
        server.store(num, '+FLAGS', '\\Deleted')
        server.expunge()


