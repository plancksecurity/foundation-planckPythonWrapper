#include "pEpmodule.hh"
#include <boost/locale.hpp>
#include <string>
#include <sstream>
#include <iomanip>
#include "basic_api.hh"
#include "message_api.hh"
#include "sync_mixin.hh"

namespace pEp {
    namespace PythonAdapter {
        using namespace std;

        static const char *version_string = "p≡p Python adapter version 0.1";
        static string about()
        {
            string version = string(version_string) + "\np≡p version "
                + PEP_VERSION + "\n";
            return version;
        }

        PEP_SESSION session = NULL;

        static void free_module(void *)
        {
            release(session);
        }

        void _throw_status(PEP_STATUS status)
        {
            if (status == PEP_STATUS_OK)
                return;
            if (status >= 0x400 && status <= 0x4ff)
                return;
            if (status == PEP_OUT_OF_MEMORY)
                throw bad_alloc();
            if (status == PEP_ILLEGAL_VALUE)
                throw invalid_argument("illegal value");

            stringstream build;
            build << setfill('0') << "p≡p 0x" << setw(4) << hex << status;
            throw runtime_error(build.str());
        }
    }
}

BOOST_PYTHON_MODULE(pEp)
{
    using namespace boost::python;
    using namespace boost::locale;
    using namespace pEp::PythonAdapter;

    docstring_options doc_options(true, false, false);

    generator gen;
    std::locale::global(gen(""));

    scope().attr("about") = about();

    auto identity_class = class_<Identity>("Identity",
    "Identity(address, username, user_id='', fpr='', comm_type=0, lang='en')\n"
    "\n"
    "represents a p≡p identity\n"
    "\n"
    "an identity is a network address, under which a user is represented in\n"
    "the network\n"
    "\n"
    "   address     network address, either an SMTP address or a URI\n"
    "   username    real name or nickname for user\n"
    "   user_id     ID this user is handled by the application\n"
    "   fpr         full fingerprint of the key being used as key ID,\n"
    "               hex encoded\n"
    "   comm_type   first rating level of this communication channel\n"
    "   lang        ISO 639-1 language code for language being preferred\n"
    "               on this communication cahnnel\n"
        )
        .def(init<string>())
        .def(init<string, string>())
        .def(init<string, string, string>())
        .def(init<string, string, string, string>())
        .def(init<string, string, string, string, int>())
        .def(init<string, string, string, string, int, string>())
        .def("__repr__", &Identity::_repr)
        .def("__str__", &Identity::_str,
    "string representation of this identity\n"
    "following the pattern 'username < address >'\n"
                )
        .add_property("address", (string(Identity::*)()) &Identity::address,
                (void(Identity::*)(string)) &Identity::address,
                "email address or URI")
        .add_property("fpr", (string(Identity::*)()) &Identity::fpr,
                (void(Identity::*)(string)) &Identity::fpr,
                "key ID (full fingerprint, hex encoded)")
        .add_property("user_id", (string(Identity::*)()) &Identity::user_id,
                (void(Identity::*)(string)) &Identity::user_id,
                "ID of person associated or 'pEp_own_userId' if own identity")
        .add_property("username", (string(Identity::*)()) &Identity::username,
                (void(Identity::*)(string)) &Identity::username,
                "name in full of person associated")
        .add_property("comm_type", (int(Identity::*)())
                (PEP_comm_type(Identity::*)()) &Identity::comm_type,
                (void(Identity::*)(int))
                (void(Identity::*)(PEP_comm_type)) &Identity::comm_type,
                 "communication type, first rating level (p≡p internal)")
        .add_property("lang", (string(Identity::*)()) &Identity::lang,
                (void(Identity::*)(string)) &Identity::lang,
                "ISO 639-1 language code")
        .add_property("me", (bool(Identity::*)()) &Identity::me,
                (void(Identity::*)(bool)) &Identity::me,
                 "true if own identity, false otherwise")
        .add_property("flags", (identity_flags_t(Identity::*)()) &Identity::flags,
                (void(Identity::*)(identity_flags_t)) &Identity::flags,
                "flags (p≡p internal)")
        .add_property("rating", &Identity::rating, "rating of Identity")
        .add_property("color", &Identity::color, "color of Identity")
        .def("__deepcopy__", &Identity::deepcopy)
        .def("__copy__", &Identity::copy);
    
    identity_class.attr("PEP_OWN_USERID") = "pEp_own_userId";

    auto blob_class = class_<Message::Blob>("Blob",
    "Blob(data, mime_type='', filename='')\n"
    "\n"
    "Binary large object\n"
    "\n"
    "   data            bytes-like object\n"
    "   mime_type       MIME type for the data\n"
    "   filename        filename to store the data\n" ,
            init< object, char const*, char const* >(args("data", "mime_type", "filename")))
        .def(init<object, string>())
        .def(init<object>())
        .def("__repr__", &Message::Blob::_repr)
        .def("__len__", &Message::Blob::size, "size of Blob data in bytes")
        .def("decode", (string(Message::Blob::*)()) &Message::Blob::decode)
        .def("decode", (string(Message::Blob::*)(string)) &Message::Blob::decode,
    "text = decode(self, encoding='')\n"
    "\n"
    "decode Blob data into string depending on MIME type if encoding=''\n"
    "\n"
    "   mime_type='application/pEp.sync'    decode as 'pEp.sync'\n"
    "   other mime_type                     decode as 'ascii' by default\n"
                )
        .add_property("mime_type", (string(Message::Blob::*)()) &Message::Blob::mime_type,
                (void(Message::Blob::*)(string)) &Message::Blob::mime_type,
                "MIME type of object in Blob")
        .add_property("filename", (string(Message::Blob::*)()) &Message::Blob::filename,
                (void(Message::Blob::*)(string)) &Message::Blob::filename,
                "filename of object in Blob");

    ((PyTypeObject *)(void *)blob_class.ptr())->tp_as_buffer = &Message::Blob::bp;

    auto message_class = class_<Message>("Message",
    "Message(dir=1, from=None)\n"
    "\n"
    "new p≡p message\n"
    "\n"
    "   dir         1 for outgoing, 2 for incoming\n"
    "   from        Identity() of sender\n"
    "\n"
    "Message(mime_text)\n"
    "\n"
    "new incoming p≡p message\n"
    "\n"
    "   mime_text       text in Multipurpose Internet Mail Extensions format\n"
                )
        .def(init<int>())
        .def(init<int, Identity *>())
        .def(init<string>())
        .def("__str__", &Message::_str,
    "the string representation of a Message is it's MIME text"
                )
        .def("__repr__", &Message::_repr)
        .add_property("dir", (int(Message::*)())
                (PEP_msg_direction(Message::*)()) &Message::dir,
                (void(Message::*)(int))
                (void(Message::*)(PEP_msg_direction)) &Message::dir,
                "0: incoming, 1: outgoing message")
        .add_property("id", (string(Message::*)()) &Message::id,
                (void(Message::*)(string)) &Message::id,
                "message ID")
        .add_property("shortmsg", (string(Message::*)()) &Message::shortmsg,
                (void(Message::*)(string)) &Message::shortmsg,
                "subject or short message")
        .add_property("longmsg", (string(Message::*)()) &Message::longmsg,
                (void(Message::*)(string)) &Message::longmsg,
                "body or long version of message")
        .add_property("longmsg_formatted", (string(Message::*)()) &Message::longmsg_formatted,
                (void(Message::*)(string)) &Message::longmsg_formatted,
                "HTML body or fromatted long version of message")
        .add_property("attachments", (boost::python::tuple(Message::*)()) &Message::attachments,
                (void(Message::*)(list)) &Message::attachments,
                "tuple of Blobs with attachments; setting moves Blobs to attachment tuple")
        .add_property("sent", (time_t(Message::*)()) &Message::sent,
                (void(Message::*)(time_t)) &Message::sent,
                "time when message was sent in UTC seconds since epoch")
        .add_property("recv", (time_t(Message::*)()) &Message::recv,
                (void(Message::*)(time_t)) &Message::recv,
                "time when message was received in UTC seconds since epoch")
        .add_property("from_", (Identity(Message::*)()) &Message::from,
                (void(Message::*)(object)) &Message::from,
                "identity where message is from")
        .add_property("to", (list(Message::*)()) &Message::to,
                (void(Message::*)(list)) &Message::to,
                "list of identities message is going to")
        .add_property("recv_by", (Identity(Message::*)()) &Message::recv_by,
                (void(Message::*)(object)) &Message::recv_by,
                "identity where message was received by")
        .add_property("cc", (list(Message::*)()) &Message::cc,
                (void(Message::*)(list)) &Message::cc,
                "list of identities message is going cc")
        .add_property("bcc", (list(Message::*)()) &Message::bcc,
                (void(Message::*)(list)) &Message::bcc,
                "list of identities message is going bcc")
        .add_property("reply_to", (list(Message::*)()) &Message::reply_to,
                (void(Message::*)(list)) &Message::reply_to,
                "list of identities where message will be replied to")
        .add_property("in_reply_to", (list(Message::*)()) &Message::in_reply_to,
                (void(Message::*)(list)) &Message::in_reply_to,
                "in_reply_to list")
        .add_property("references", (list(Message::*)()) &Message::references,
                (void(Message::*)(list)) &Message::references,
                "message IDs of messages this one is referring to")
        .add_property("keywords", (list(Message::*)()) &Message::keywords,
                (void(Message::*)(list)) &Message::keywords,
                "keywords this message should be stored under")
        .add_property("comments", (string(Message::*)()) &Message::comments,
                (void(Message::*)(string)) &Message::comments,
                "comments added to message")
        .add_property("opt_fields", (dict(Message::*)()) &Message::opt_fields,
                (void(Message::*)(dict)) &Message::opt_fields,
                "opt_fields of message")
        .add_property("enc_format", (int(Message::*)())
                (PEP_enc_format(Message::*)()) &Message::enc_format,
                (void(Message::*)(int))
                (void(Message::*)(PEP_enc_format)) &Message::enc_format,
                "0: unencrypted, 1: inline PGP, 2: S/MIME, 3: PGP/MIME, 4: p≡p format")
        .def("encrypt", (Message(Message::*)())&Message::encrypt)
        .def("encrypt", (Message(Message::*)(list))&Message::encrypt)
        .def("encrypt", (Message(Message::*)(list,string))&Message::encrypt)
        .def("encrypt", (Message(Message::*)(list,string,int))&Message::encrypt)
        .def("encrypt", (Message(Message::*)(list,int))&Message::_encrypt)
        .def("encrypt", (Message(Message::*)(list,int,int))&Message::_encrypt,
    "msg = encrypt(self, extra_keys=[], enc_format='pEp', flags=0)\n"
    "\n"
    "encrypts a p≡p message and returns the encrypted message\n"
    "\n"
    "   extra_keys      list of strings with fingerprints for extra keys to use\n"
    "                   for encryption\n"
    "   enc_format      'none' or 0, 'partitioned' or 1, 'S/MIME' or 2,\n"
    "                   'PGP/MIME' or 3, 'pEp' or 4\n"
    "   flags           1 is force encryption\n"
                )
        .def("decrypt", &Message::decrypt,
    "msg, keys, rating, flags = decrypt()\n"
    "\n"
    "decrypts a p≡p message and returns a tuple with data\n"
    "\n"
    "   msg             the decrypted p≡p message\n"
    "   keys            a list of keys being used\n"
    "   rating          the rating of the message as integer\n"
    "   flags           flags set while decryption (reserved)\n"
                )
        .add_property("outgoing_rating", &Message::outgoing_rating, "rating outgoing message will have")
        .add_property("outgoing_color", &Message::outgoing_color, "color outgoing message will have")
        .def("__deepcopy__", &Message::deepcopy)
        .def("__copy__", &Message::copy);

    // basic API

    def("update_identity", &update_identity,
    "update_identity(ident)\n"
    "\n"
    "update identity information\n"
    "call this to complete identity information when you at least have an address\n"
            );
    def("myself", &myself,
    "myself(ident)\n"
    "\n"
    "ensures that the own identity is being complete\n"
    "supply ident.address and ident.username\n"
            );

    // message API

    def("incoming_message", &incoming_message,
    "msg = incoming_message(mime_text)\n"
    "\n"
    "create an incoming message from a MIME text"
            );
    def("outgoing_message", &outgoing_message,
    "msg = outgoing_message(ident)\n"
    "\n"
    "create an outgoing message using an own identity"
            );
    def("color", &_color,
    "c = color(rating)\n"
    "\n"
    "calculate color value out of rating"
            );
    def("trustwords", &_trustwords,
    "text = trustwords(ident_own, ident_partner)\n"
    "\n"
    "calculate trustwords for two Identities");
    def("config_keep_sync_msg", &_config_keep_sync_msg,
    "config_keep_sync_msg(enabled)\n"
    "\n"
    "configure if sync messages are being kept or automatically removed (default)");

    // key sync API

    auto sync_mixin_class = class_<SyncMixIn, SyncMixIn_callback, boost::noncopyable>(
            "SyncMixIn",
    "class MySyncHandler(SyncMixIn)\n"
    "   def messageToSend(self, msg):\n"
    "       ...\n"
    "\n"
    "   def showHandshake(self, me, partner):\n"
    "       ...\n"
    "\n"
    "p≡p Sync MixIn\n"
    "\n"
    "write a handler class to enable p≡p sync protocol\n")
        .def("messageToSend", &SyncMixIn::messageToSend,
    "messageToSend(self, msg)"
    "\n"
    "   msg             p≡p message to send\n"
    "\n"
    "overwrite this method with code actually sending msg")
        .def("showHandshake", &SyncMixIn::showHandshake,
    "showHandshake(self, me, partner)\n"
    "\n"
    "   me              own identity\n"
    "   partner         identity of communication partner\n"
    "\n"
    "overwrite this method with code showing a trustwords dialog")
#ifndef NDEBUG
        .def("inject", &SyncMixIn::_inject,
    "inject(self, event, partner, extra)\n"
    "\n"
    "   event           number of event to inject\n"
    "   partner         identity of communication partner\n"
    "   extra           optional extra data or None\n"
    "\n"
    "inject an event into the sync state machine (for debugging purposes only)")
#endif
        .def("deliverHandshakeResult", &SyncMixIn::deliverHandshakeResult,
    "deliverHandshakeResult(self, result)\n"
    "\n"
    "   result          -1: cancel, 0: accepted, 1: rejected\n"
    "\n"
    "call to deliver the handshake result");

    // codecs

    call< object >(((object)(import("codecs").attr("register"))).ptr(), make_function(sync_search));

    // init() and release()

    PyModuleDef * _def = PyModule_GetDef(scope().ptr());
    _def->m_free = free_module;

    PEP_STATUS status = ::init(&session);
    if (status != PEP_STATUS_OK) {
        stringstream ss;
        ss << "init session failed with error " << status;
        string s;
        ss >> s;
        throw runtime_error(s);
    }
}

