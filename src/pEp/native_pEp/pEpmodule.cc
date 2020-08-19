// This file is under GNU Affero General Public License 3.0
// see LICENSE.txt

#include <boost/python.hpp>
#include <boost/locale.hpp>
#include <string>
#include <sstream>
#include <iomanip>
#include <mutex>

#include <pEp/Adapter.hh>
#include <pEp/key_reset.h>
#include <pEp/message_api.h>
#include <pEp/sync_api.h>
#include <pEp/status_to_string.h>

#include "pEpmodule.hh"
#include "basic_api.hh"
#include "message_api.hh"
#include "user_interface.hh"


namespace pEp {
    namespace PythonAdapter {
        using namespace std;

//        Adapter adapter(true);

        void config_passive_mode(bool enable)
        {
            ::config_passive_mode(pEp::Adapter::session(), enable);
        }

        void config_unencrypted_subject(bool enable)
        {
            ::config_unencrypted_subject(pEp::Adapter::session(), enable);
        }

        void key_reset_user(string user_id, string fpr)
        {
            if (user_id == "")
                throw invalid_argument("user_id required");

            PEP_STATUS status = ::key_reset_user(pEp::Adapter::session(),
                    user_id.c_str(), fpr != "" ?  fpr.c_str() : nullptr);
            _throw_status(status);
        }

        void key_reset_user2(string user_id)
        {
            key_reset_user(user_id, "");
        }

        void key_reset_all_own_keys()
        {
            PEP_STATUS status = ::key_reset_all_own_keys(pEp::Adapter::session());
            _throw_status(status);
        }

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

            if (string(pEp_status_to_string(status)) == "unknown status code") {
                stringstream build;
                build << setfill('0') << "p≡p 0x" << setw(4) << hex << status;
                throw runtime_error(build.str());
            }
            else {
                throw runtime_error(pEp_status_to_string(status));
            }
        }

        PEP_STATUS _ensure_passphrase(PEP_SESSION session, const char *fpr)
        {
            return PEP_STATUS_OK;
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

//        void do_sync_protocol()
//        {
//            ::do_sync_protocol(pEp::Adapter::session(), nullptr);
//        }

        void shutdown_sync()
        {
            pEp::Adapter::shutdown();
        }

        void debug_color(int ansi_color)
        {
            ::set_debug_color(pEp::Adapter::session(), ansi_color);
        }

        void leave_device_group() {
            ::leave_device_group(pEp::Adapter::session());
        }

//        void script_is_implementing_sync() {
//            adapter.script_is_implementing_sync();
//        }

        bool is_sync_active() {
            return pEp::Adapter::is_sync_running();
        }
    }
}

BOOST_PYTHON_MODULE(native_pEp)
{
    using namespace boost::python;
    using namespace boost::locale;
    using namespace pEp::PythonAdapter;

    docstring_options doc_options(true, false, false);

    generator gen;
    std::locale::global(gen(""));
    _scope = new scope();

    scope().attr("about") = about();
    scope().attr("per_user_directory") = per_user_directory();
    scope().attr("per_machine_directory") = per_machine_directory();
    scope().attr("engine_version") = get_engine_version();
    scope().attr("protocol_version") = get_protocol_version();

    def("passive_mode", pEp::PythonAdapter::config_passive_mode,
            "do not attach pub keys to all messages");

    def("unencrypted_subject", pEp::PythonAdapter::config_unencrypted_subject,
            "do not encrypt the subject of messages");

    def("key_reset", pEp::PythonAdapter::key_reset_user,
            "reset the default database status for the user / keypair provided\n"
            "This will effectively perform key_reset on each identity\n"
            "associated with the key and user_id, if a key is provided, and for\n"
            "each key (and all of their identities) if an fpr is not.");

    def("key_reset", pEp::PythonAdapter::key_reset_user2,
            "reset the default database status for the user / keypair provided\n"
            "This will effectively perform key_reset on each identity\n"
            "associated with the key and user_id, if a key is provided, and for\n"
            "each key (and all of their identities) if an fpr is not.");

    def("key_reset_all_own_keys", pEp::PythonAdapter::key_reset_all_own_keys,
            "revoke and mistrust all own keys, generate new keys for all\n"
            "own identities, and opportunistically communicate key reset\n"
            "information to people we have recently contacted.");

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
        .def("key_reset", &pEp::PythonAdapter::Identity::key_reset,
                boost::python::arg("fpr")=object(""),
            "reset the default database status for the identity / keypair provided. If this\n"
            "corresponds to the own user and a private key, also revoke the key, generate a\n"
            "new one, and communicate the reset to recently contacted pEp partners for this\n"
            "identity. If it does not, remove the key from the keyring; the key's status is\n"
            "completely fresh on next contact from the partner.")

        .def("key_mistrusted", &pEp::PythonAdapter::Identity::key_mistrusted,
                boost::python::arg("fpr")=object(""),
            "If you want updated trust on the identity, you ll have"
            "to call update_identity or myself respectively after this."
            "N.B. If you are calling this on a key that is the identity or user default,"
            "it will be removed as the default key for ANY identity and user for which"
            "it is the default. Please keep in mind that the undo in undo_last_mistrust"
            "will only undo the current identity's / it's user's default, not any"
            "other identities which may be impacted (this will not affect most use cases)")

        .def("enable_for_sync", &pEp::PythonAdapter::Identity::enable_for_sync,
                "Enable own identity for p≡p sync.\n\n"
                "Only use this on own identities, which are used as accounts.\n")
        .def("disable_for_sync", &pEp::PythonAdapter::Identity::disable_for_sync,
                "Disable own identity for p≡p sync.\n\n"
                "Only use this on own identities, which are used as accounts.\n")

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
        .add_property("color", &pEp::PythonAdapter::Identity::color, "color of Identity as PEP_color")
        .add_property("is_pEp_user", &pEp::PythonAdapter::Identity::is_pEp_user, "True if this is an identity of a pEp user")
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
    "   mime_type='application/pEp.sync'      decode as 'pEp.sync'\n"
    "   mime_type='application/pEp.keyreset'  decode as 'pEp.keyreset'\n"
    "   other mime_type                       decode as 'ascii' by default\n"
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
        .def("decrypt", &Message::decrypt, boost::python::arg("flags")=0,
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
        .add_property("outgoing_color", &Message::outgoing_color, "color outgoing message will have as PEP_color")
        .def("__deepcopy__", &Message::deepcopy)
        .def("__copy__", &Message::copy);

    // basic API and key management API

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

    def("key_reset_trust", &pEp::PythonAdapter::key_reset_trust,
            "key_reset_trust(ident)\n"
            "\n"
            "reset trust bit or explicitly mistrusted status for an identity and "
            "its accompanying key/user_id pair\n"
        );

    def("import_key", &pEp::PythonAdapter::import_key,
            "private_key_list = import_key(key_data)\n"
            "\n"
            "import key(s) from key_data\n"
        );

    def("export_key", &pEp::PythonAdapter::export_key,
            "key_data = export_key(identity)\n"
            "\n"
            "export key(s) of identity\n"
        );

    def("export_secret_key", &pEp::PythonAdapter::export_secret_key,
            "key_data = export_seret_key(identity)\n"
            "\n"
            "export secret key(s) of identity\n"
        );

    def("set_own_key", &pEp::PythonAdapter::set_own_key,
            "set_own_key(me, fpr)\n"
            "\n"
            "mark a key as an own key, and make it the default key\n"
            "\n"
            "me         Own identity for which to add the existing key\n"
            "fpr        The fingerprint of the key to be added\n"
            "\n"
            "me->address, me->user_id and me->username must be set to valid data\n"
            "myself() is called by set_own_key() without key generation\n"
            "me->flags are ignored\n"
            "me->address must not be an alias\n"
            "me->fpr will be ignored and replaced by fpr\n"
        );

    // message API

    enum_<PEP_rating>("rating")
        .value("_undefined", PEP_rating_undefined)
        .value("cannot_decrypt", PEP_rating_cannot_decrypt)
        .value("have_no_key", PEP_rating_have_no_key)
        .value("unencrypted", PEP_rating_unencrypted)
        .value("unreliable", PEP_rating_unreliable)
        .value("reliable", PEP_rating_reliable)
        .value("trusted", PEP_rating_trusted)
        .value("trusted_and_anonymized", PEP_rating_trusted_and_anonymized)
        .value("fully_anonymous", PEP_rating_fully_anonymous)
        .value("mistrust", PEP_rating_mistrust)
        .value("b0rken", PEP_rating_b0rken)
        .value("under_attack", PEP_rating_under_attack);

    enum_<PEP_color>("colorvalue")
        .value("no_color", PEP_color_no_color)
        .value("yellow", PEP_color_yellow)
        .value("green", PEP_color_green)
        .value("red", PEP_color_red);


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
    "calculate color value out of rating. Returns PEP_color"
            );
    def("trustwords", &_trustwords,
    "text = trustwords(ident_own, ident_partner)\n"
    "\n"
    "calculate trustwords for two Identities");

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
        .value("SYNC_NOTIFY_TIMEOUT"               , SYNC_NOTIFY_TIMEOUT)
        .value("SYNC_NOTIFY_ACCEPTED_DEVICE_ADDED" , SYNC_NOTIFY_ACCEPTED_DEVICE_ADDED)
        .value("SYNC_NOTIFY_ACCEPTED_GROUP_CREATED", SYNC_NOTIFY_ACCEPTED_GROUP_CREATED)
        .value("SYNC_NOTIFY_ACCEPTED_DEVICE_ACCEPTED", SYNC_NOTIFY_ACCEPTED_DEVICE_ACCEPTED)
        .value("SYNC_NOTIFY_SOLE"                  , SYNC_NOTIFY_SOLE)
        .value("SYNC_NOTIFY_IN_GROUP"              , SYNC_NOTIFY_IN_GROUP);

//    auto user_interface_class = class_<UserInterface, UserInterface_callback, boost::noncopyable>(
//            "UserInterface",
//    "class MyUserInterface(UserInterface):\n"
//    "   def notifyHandshake(self, me, partner):\n"
//    "       ...\n"
//    "\n"
//    "p≡p User Interface class\n"
//    "To be used as a mixin\n"
//    )
//        .def("notifyHandshake", &UserInterface::notifyHandshake,
//    "notifyHandshake(self, me, partner)\n"
//    "\n"
//    "   me              own identity\n"
//    "   partner         identity of communication partner\n"
//    "\n"
//    "overwrite this method with an implementation of a handshake dialog")
//        .def("deliverHandshakeResult", &UserInterface::deliverHandshakeResult,
//                boost::python::arg("identities")=object(),
//    "deliverHandshakeResult(self, result, identities=None)\n"
//    "\n"
//    "   result          -1: cancel, 0: accepted, 1: rejected\n"
//    "   identities      list of identities to share or None for all\n"
//    "\n"
//    "call to deliver the handshake result of the handshake dialog")
//    ;


// TODO: Replace with start_sync()
//    def("do_sync_protocol", &pEp::PythonAdapter::do_sync_protocol,
//        "do_sync_protocol()\n"
//        "\n"
//        "in case of an explicit sync thread instead of a single threaded\n"
//        "implementation call this function in your sync thread\n"
//    );

    def("shutdown_sync", &pEp::PythonAdapter::shutdown_sync,
            "shutdown_sync()\n"
            "\n"
            "call this from another thread to shut down the sync thread\n"
       );

    def("debug_color", &pEp::PythonAdapter::debug_color,
            "for debug builds set ANSI color value");

    def("leave_device_group", &pEp::PythonAdapter::leave_device_group,
            "leave_device_group()\n"
            "\n"
            "call this for a grouped device, which should leave\n"
       );
    
//    def("script_is_implementing_sync", &pEp::PythonAdapter::script_is_implementing_sync,
//            "script_is_implementing_sync()\n"
//            "\n"
//            "call this in case the Python script is implementing sync to make\n"
//            "is_sync_active() working\n"
//       );

    def("is_sync_active", &pEp::PythonAdapter::is_sync_active,
            "is_sync_active()\n"
            "\n"
            "True if sync is active, False otherwise\n"
       );


    // codecs
    call< object >(((object)(import("codecs").attr("register"))).ptr(), make_function(sync_search));
    call< object >(((object)(import("codecs").attr("register"))).ptr(), make_function(distribution_search));
}
