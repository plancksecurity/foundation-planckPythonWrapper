#/!usr/bin/env python3
#
# Copyleft 2020, p≡p Security
# Copyleft 2020, Hartmut Goebel <h.goebel@crazy-compilers.com>
#
# This file is under GNU General Public License 3.0
"""
This examples shows how to transport pEp messages within a
simple XML based message format which is capable for attachments.

pEp message elements loosely follow the "pEp for XML specification" and
https://pEp.software/ns/pEp-1.0.xsd.

IMPORTANT: In this example, no error checking is done. Neither is
           the "pEp for XML" specification enforced.

Structure of the simple XML based message:
<msg>
  <from>from-addr</from>
  <to>to-addr</to>
  <body>text of the messgage (must not be XML)</bod>
  <attachments>
    <attachment>textual data</attachment>
    …
  <attachments>
</msg>
"""

from lxml import etree
import email.utils
import pEp

__all__ = ["serialize_pEp_message", "parse_serialized_message"]

CT2TAG = {
    'application/pgp-keys': 'keydata',
    'application/pEp.sync': 'sync',
    'application/pEp.distribution': 'distribution',
    'application/pgp-signature': 'signature',
}

TAG2CT = dict((v,k)for (k,v) in CT2TAG.items())

PEP_NAMESPACE = "https://pEp.software/ns/pEp-1.0.xsd"
PEP_NS = '{%s}' % PEP_NAMESPACE
NSMAP = {'pEp': PEP_NAMESPACE}

INCOMING = 0
OUTGOING = 1

UNENCRYPTED = 0

def serialize_pEp_message(msg):
    root = etree.Element("msg", nsmap=NSMAP)
    etree.SubElement(root, "to").text = str(msg.to[0])
    etree.SubElement(root, "from").text = str(msg.from_)

    if msg.enc_format == UNENCRYPTED:
        # unencrypted
        etree.SubElement(root, "body").text = msg.longmsg
        attachments = etree.SubElement(root, "attachments")
        # FIXME: Namespace
        attachments = etree.SubElement(attachments,
                                       PEP_NS + "attachments",
                                       version=msg.opt_fields['X-pEp-Version'])
        # TODO: opt_fields, esp. auto-consume
        # TODO: Order pEp attachments by type
        for attach in msg.attachments:
            # no need to base64-encode, attachement are ascii-armoured
            # already
            #attachment = base64_encode(attachment)
            # FIXME: Namespace
            a = etree.SubElement(attachments,
                                 PEP_NS + CT2TAG[attach.mime_type])
            a.text = attach.decode("ascii")
    else: # encrypted
        # forget about longmsg and original body
        # encrypted message is an attachment and there might be
        # further attachments, e.g. new keys
        # build a new message out of these attachments
        etree.SubElement(root, "body") # emptry body
        attachments = etree.SubElement(root, "attachments")
        assert len(msg.attachments) == 2
        # first attachment is "Version: 1"
        attach = msg.attachments[1]
        # no need to base64-encode, attachements are ascii-armoured
        # already
        n = etree.SubElement(root, PEP_NS + "message")
        n.text = attach.decode("ascii")
    return etree.tostring(root)


def parse_serialized_message(transport_message):

    def addr2identity(text):
        name, addr = email.utils.parseaddr(text)
        ident = pEp.Identity(addr, name)
        ident.update()
        return ident

    # parse the XML text, fetch from and to
    root = etree.fromstring(transport_message)
    from_ = addr2identity(root.xpath("./from/text()")[0])
    msg1 = pEp.Message(INCOMING, from_)
    msg1.to.append(addr2identity(root.xpath("./to/text()")[0]))
    enc_msg = root.find("{%s}message" % PEP_NAMESPACE)
    if enc_msg is not None:
        # this is an encrypted message, ignore all but the encrypted message
        msg1.attachments = [
            # As of Engine r4652 the encrypted message must be the second
            # attachment
            pEp.Blob(b"Version: 1", "application/pgp-encrypted"),
            pEp.Blob(enc_msg.text.encode(), "application/xxpgp-encrypted")]
    else:
        # this is an unencrypted message, might contain pEp attachments
        msg1.longmsg = root.findtext("body")
        pEp_attachments = None
        attachments = root.find("attachments")
        if attachments is not None:
            pEp_attachments = attachments.find("{%s}attachments" % PEP_NAMESPACE)
        if pEp_attachments is not None:
            msg1.opt_fields['X-pEp-Version'] = pEp_attachments.attrib["version"]
            pEp_attachs = []
            for tagname in ("keydata", "signature", "sync", "distribution"):
                for attach in pEp_attachments.iterfind(
                    "{%s}%s" % (PEP_NAMESPACE, tagname)):
                    pEp_attachs.append(
                        pEp.Blob(attach.text.encode(), TAG2CT[tagname]))
            msg1.attachments = pEp_attachs
    msg2, keys, flags = msg1.decrypt()
    return msg2, msg2.rating
