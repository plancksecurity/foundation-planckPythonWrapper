// This file is under GNU Affero General Public License 3.0
// see LICENSE.txt

#include "pEpmodule.hh"
#include <boost/locale.hpp>
#include <string>
#include <sstream>
#include <iomanip>
#include "basic_api.hh"
#include "message_api.hh"
#include "user_interface.hh"
#include "adapter.hh"

#include <mutex>

#include <pEp/message_api.h>
#include <pEp/sync_api.h>

namespace pEp {
    namespace PythonAdapter {
        using namespace std;

        Adapter adapter(true);
        scope *_scope = NULL;

        static const char *version_string = "p≡p Python adapter version 0.3";
        static string about()
        {
            string version = string(version_string) + "\np≡p version "
                + PEP_VERSION + "\n";
            return version;
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

        PEP_STATUS _messageToSend(::message *msg)
        {
            if (!_scope)
                return PEP_SEND_FUNCTION_NOT_REGISTERED;

            try {
                object m = _scope->attr("messageToSend");
                call< void >(m.ptr(), Message(msg));
            }
            catch (exception& e) { }

            return PEP_STATUS_OK;
        }

        void messageToSend(Message msg) {
            throw runtime_error("implement pEp.messageToSend(msg)");
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
    _scope = new scope();

    scope().attr("about") = about();
    
    auto identity_class = class_<pEp::PythonAdapter::Identity>("Identity",
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
    "               on this communication channel\n"
        )
        .def(boost::python::init<string>())
        .def(boost::python::init<string, string>())
        .def(boost::python::init<string, string, string>())
        .def(boost::python::init<string, string, string, string>())
        .def(boost::python::init<string, string, string, string, int>())
        .def(boost::python::init<string, string, string, string, int, string>())
        .def("__repr__", &pEp::PythonAdapter::Identity::_repr)
        .def("__str__", &pEp::PythonAdapter::Identity::_str,
    "string representation of this identity\n"
    "following the pattern 'username < address >'\n"
                )
        .add_property("address", (string(pEp::PythonAdapter::Identity::*)()) &pEp::PythonAdapter::Identity::address,
                (void(pEp::PythonAdapter::Identity::*)(string)) &pEp::PythonAdapter::Identity::address,
                "email address or URI")
        .add_property("fpr", (string(pEp::PythonAdapter::Identity::*)()) &pEp::PythonAdapter::Identity::fpr,
                (void(pEp::PythonAdapter::Identity::*)(string)) &pEp::PythonAdapter::Identity::fpr,
                "key ID (full fingerprint, hex encoded)")
        .add_property("user_id", (string(pEp::PythonAdapter::Identity::*)()) &pEp::PythonAdapter::Identity::user_id,
                (void(pEp::PythonAdapter::Identity::*)(string)) &pEp::PythonAdapter::Identity::user_id,
                "ID of person associated or 'pEp_own_userId' if own identity")
        .add_property("username", (string(pEp::PythonAdapter::Identity::*)()) &pEp::PythonAdapter::Identity::username,
                (void(pEp::PythonAdapter::Identity::*)(string)) &pEp::PythonAdapter::Identity::username,
                "name in full of person associated")
        .add_property("comm_type", (int(pEp::PythonAdapter::Identity::*)())
                (PEP_comm_type(pEp::PythonAdapter::Identity::*)()) &pEp::PythonAdapter::Identity::comm_type,
                (void(pEp::PythonAdapter::Identity::*)(int))
                (void(pEp::PythonAdapter::Identity::*)(PEP_comm_type)) &pEp::PythonAdapter::Identity::comm_type,
                 "communication type, first rating level (p≡p internal)")
        .add_property("lang", (string(pEp::PythonAdapter::Identity::*)()) &pEp::PythonAdapter::Identity::lang,
                (void(pEp::PythonAdapter::Identity::*)(string)) &pEp::PythonAdapter::Identity::lang,
                "ISO 639-1 language code")
        .add_property("flags", (identity_flags_t(pEp::PythonAdapter::Identity::*)()) &pEp::PythonAdapter::Identity::flags,
                (void(pEp::PythonAdapter::Identity::*)(identity_flags_t)) &pEp::PythonAdapter::Identity::flags,
                "flags (p≡p internal)")
        .add_property("rating", &pEp::PythonAdapter::Identity::rating, "rating of Identity")
        .add_property("color", &pEp::PythonAdapter::Identity::color, "color of Identity")
        .def("__deepcopy__", &pEp::PythonAdapter::Identity::deepcopy)
        .def("update", &pEp::PythonAdapter::Identity::update, "update Identity")
        .def("__copy__", &pEp::PythonAdapter::Identity::copy);
    
    identity_class.attr("PEP_OWN_USERID") = "pEp_own_userId";

    auto blob_class = class_<Message::Blob>("Blob",
    "Blob(data, mime_type='', filename='')\n"
    "\n"
    "Binary large object\n"
    "\n"
    "   data            bytes-like object\n"
    "   mime_type       MIME type for the data\n"
    "   filename        filename to store the data\n" ,
            boost::python::init< object, char const*, char const* >(args("data", "mime_type", "filename")))
        .def(boost::python::init<object, string>())
        .def(boost::python::init<object>())
        .def("__repr__", &Message::Blob::_repr)
        .def("__len__", &Message::Blob::size, "size of Blob data in bytes")
        .def("decode", (string(Message::Blob::*)()) &Message::Blob::decode)
        .def("decode", (string(Message::Blob::*)(string)) &Message::Blob::decode,
    "text = blob.decode(encoding='')\n"
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
        .def(boost::python::init<int>())
        .def(boost::python::init<int, pEp::PythonAdapter::Identity *>())
        .def(boost::python::init<string>())
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
                (void(Message::*)(boost::python::list)) &Message::attachments,
                "tuple of Blobs with attachments; setting moves Blobs to attachment tuple")
        .add_property("sent", (time_t(Message::*)()) &Message::sent,
                (void(Message::*)(time_t)) &Message::sent,
                "time when message was sent in UTC seconds since epoch")
        .add_property("recv", (time_t(Message::*)()) &Message::recv,
                (void(Message::*)(time_t)) &Message::recv,
                "time when message was received in UTC seconds since epoch")
        .add_property("from_", (pEp::PythonAdapter::Identity(Message::*)()) &Message::from,
                (void(Message::*)(object)) &Message::from,
                "identity where message is from")
        .add_property("to", (boost::python::list(Message::*)()) &Message::to,
                (void(Message::*)(boost::python::list)) &Message::to,
                "list of identities message is going to")
        .add_property("recv_by", (pEp::PythonAdapter::Identity(Message::*)()) &Message::recv_by,
                (void(Message::*)(object)) &Message::recv_by,
                "identity where message was received by")
        .add_property("cc", (boost::python::list(Message::*)()) &Message::cc,
                (void(Message::*)(boost::python::list)) &Message::cc,
                "list of identities message is going cc")
        .add_property("bcc", (boost::python::list(Message::*)()) &Message::bcc,
                (void(Message::*)(boost::python::list)) &Message::bcc,
                "list of identities message is going bcc")
        .add_property("reply_to", (boost::python::list(Message::*)()) &Message::reply_to,
                (void(Message::*)(boost::python::list)) &Message::reply_to,
                "list of identities where message will be replied to")
        .add_property("in_reply_to", (boost::python::list(Message::*)()) &Message::in_reply_to,
                (void(Message::*)(boost::python::list)) &Message::in_reply_to,
                "in_reply_to list")
        .add_property("references", (boost::python::list(Message::*)()) &Message::references,
                (void(Message::*)(boost::python::list)) &Message::references,
                "message IDs of messages this one is referring to")
        .add_property("keywords", (boost::python::list(Message::*)()) &Message::keywords,
                (void(Message::*)(boost::python::list)) &Message::keywords,
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
        .def("encrypt", (Message(Message::*)(boost::python::list))&Message::_encrypt)
        .def("encrypt", (Message(Message::*)(boost::python::list,int))&Message::_encrypt)
        .def("encrypt", (Message(Message::*)(boost::python::list,int,int))&Message::_encrypt,
    "msg2 = msg1.encrypt(extra_keys=[], enc_format='pEp', flags=0)\n"
    "\n"
    "encrypts a p≡p message and returns the encrypted message\n"
    "\n"
    "   extra_keys      list of strings with fingerprints for extra keys to use\n"
    "                   for encryption\n"
    "   enc_format      0 for none, 1 for partitioned, 2 for S/MIME,\n"
    "                   3 for PGP/MIME, 4 for pEp\n"
    "   flags           1 is force encryption\n"
                )
        .def("decrypt", &Message::decrypt,
    "msg2, keys, rating, flags = msg1.decrypt()\n"
    "\n"
    "decrypts a p≡p message and returns a tuple with data\n"
    "\n"
    "   msg             the decrypted p≡p message\n"
    "   keys            a list of keys being used\n"
    "   rating          the rating of the message as integer\n"
    "   flags           flags set while decryption\n"
                )
        .add_property("outgoing_rating", &Message::outgoing_rating, "rating outgoing message will have")
        .add_property("outgoing_color", &Message::outgoing_color, "color outgoing message will have")
        .def("__deepcopy__", &Message::deepcopy)
        .def("__copy__", &Message::copy);

    // basic API

    def("update_identity", &pEp::PythonAdapter::update_identity,
    "update_identity(ident)\n"
    "\n"
    "update identity information\n"
    "call this to complete identity information when you at least have an address\n"
            );
    def("myself", &pEp::PythonAdapter::myself,
    "myself(ident)\n"
    "\n"
    "ensures that the own identity is being complete\n"
    "supply ident.address and ident.username\n"
            );
    def("trust_personal_key", &pEp::PythonAdapter::trust_personal_key,
    "trust_personal_key(ident)\n"
    "\n"
    "mark a key as trusted with a person\n"
            );

    enum_<identity_flags>("identity_flags")
        .value("PEP_idf_not_for_sync", PEP_idf_not_for_sync)
        .value("PEP_idf_list", PEP_idf_list)
        .value("PEP_idf_devicegroup", PEP_idf_devicegroup);

    def("set_identity_flags", &pEp::PythonAdapter::set_identity_flags,
    "set_identity_flags(ident, flags)\n"
    "\n"
    "set identity flags\n"
            );

    def("unset_identity_flags", &pEp::PythonAdapter::unset_identity_flags,
    "unset_identity_flags(ident, flags)\n"
    "\n"
    "unset identity flags\n"
            );

    // message API

    enum_<PEP_rating>("PEP_rating")
        .value("PEP_rating_undefined", PEP_rating_undefined)
        .value("PEP_rating_cannot_decrypt", PEP_rating_cannot_decrypt)
        .value("PEP_rating_have_no_key", PEP_rating_have_no_key)
        .value("PEP_rating_unencrypted", PEP_rating_unencrypted)
        .value("PEP_rating_unencrypted_for_some", PEP_rating_unencrypted_for_some)
        .value("PEP_rating_unreliable", PEP_rating_unreliable)
        .value("PEP_rating_reliable", PEP_rating_reliable)
        .value("PEP_rating_trusted", PEP_rating_trusted)
        .value("PEP_rating_trusted_and_anonymized", PEP_rating_trusted_and_anonymized)
        .value("PEP_rating_fully_anonymous", PEP_rating_fully_anonymous)
        .value("PEP_rating_mistrust", PEP_rating_mistrust)
        .value("PEP_rating_b0rken", PEP_rating_b0rken)
        .value("PEP_rating_under_attack", PEP_rating_under_attack);

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

    // messageToSend()

    def("messageToSend", &pEp::PythonAdapter::messageToSend,
    "messageToSend(msg)\n"
    "\n"
    "override pEp.messageToSend(msg) with your own implementation\n"
    "this callback is being called when a p≡p management message needs to be sent");

    // Sync API

    enum_<sync_handshake_signal>("sync_handshake_signal")
        .value("SYNC_NOTIFY_UNDEFINED"             , SYNC_NOTIFY_UNDEFINED)
        .value("SYNC_NOTIFY_INIT_ADD_OUR_DEVICE"   , SYNC_NOTIFY_INIT_ADD_OUR_DEVICE)
        .value("SYNC_NOTIFY_INIT_ADD_OTHER_DEVICE" , SYNC_NOTIFY_INIT_ADD_OTHER_DEVICE)
        .value("SYNC_NOTIFY_INIT_FORM_GROUP"       , SYNC_NOTIFY_INIT_FORM_GROUP)
        .value("SYNC_NOTIFY_INIT_MOVE_OUR_DEVICE"  , SYNC_NOTIFY_INIT_MOVE_OUR_DEVICE)
        .value("SYNC_NOTIFY_TIMEOUT"               , SYNC_NOTIFY_TIMEOUT)
        .value("SYNC_NOTIFY_ACCEPTED_DEVICE_ADDED" , SYNC_NOTIFY_ACCEPTED_DEVICE_ADDED)
        .value("SYNC_NOTIFY_ACCEPTED_GROUP_CREATED", SYNC_NOTIFY_ACCEPTED_GROUP_CREATED)
        .value("SYNC_NOTIFY_ACCEPTED_DEVICE_MOVED" , SYNC_NOTIFY_ACCEPTED_DEVICE_MOVED)
        .value("SYNC_NOTIFY_OVERTAKEN"             , SYNC_NOTIFY_OVERTAKEN);

    auto user_interface_class = class_<UserInterface, UserInterface_callback, boost::noncopyable>(
            "UserInterface",
    "class MyUserInterface(UserInterface):\n"
    "   def notifyHandshake(self, me, partner):\n"
    "       ...\n"
    "\n"
    "p≡p User Interface class\n"
    "To be used as a mixin\n"
    )
        .def("notifyHandshake", &UserInterface::notifyHandshake,
    "notifyHandshake(self, me, partner)\n"
    "\n"
    "   me              own identity\n"
    "   partner         identity of communication partner\n"
    "\n"
    "overwrite this method with an implementation of a handshake dialog")
        .def("deliverHandshakeResult", &UserInterface::deliverHandshakeResult,
    "deliverHandshakeResult(self, partber, result)\n"
    "\n"
    "   partner         identity of communication partner\n"
    "   result          -1: cancel, 0: accepted, 1: rejected\n"
    "\n"
    "call to deliver the handshake result of the handshake dialog")
    ;

    // codecs

    call< object >(((object)(import("codecs").attr("register"))).ptr(), make_function(sync_search));
}

