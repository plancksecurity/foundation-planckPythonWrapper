#include "pEpmodule.hh"
#include <boost/locale.hpp>
#include <string>
#include <sstream>
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
            build << "p≡p error: " << status;
            throw runtime_error(build.str());
        }
    }
}

BOOST_PYTHON_MODULE(pEp)
{
    using namespace boost::python;
    using namespace boost::locale;
    using namespace pEp::PythonAdapter;

    docstring_options doc_options(true, true, false);

    generator gen;
    std::locale::global(gen(""));

    scope().attr("about") = about();

    auto identity_class = class_<Identity>("Identity", "p≡p identity")
        .def(init<string>())
        .def(init<string, string>())
        .def(init<string, string, string>())
        .def(init<string, string, string, string>())
        .def(init<string, string, string, string, int>())
        .def(init<string, string, string, string, int, string>())
        .def("__repr__", &Identity::_repr)
        .def("__str__", &Identity::_str)
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
                 "communication type (p≡p internal)")
        .add_property("lang", (string(Identity::*)()) &Identity::lang,
                (void(Identity::*)(string)) &Identity::lang,
                "ISO 639-1 language code")
        .add_property("me", (bool(Identity::*)()) &Identity::me,
                (void(Identity::*)(bool)) &Identity::me,
                 "true if own identity, false otherwise")
        .add_property("flags", (identity_flags_t(Identity::*)()) &Identity::flags,
                (void(Identity::*)(identity_flags_t)) &Identity::flags,
                "flags (p≡p internal)");
    
    identity_class.attr("PEP_OWN_USERID") = "pEp_own_userId";

    auto blob_class = class_<Message::Blob>("Blob", "Binary large object",
            init< object, char const*, char const* >(args("data", "mime_type", "filename"),
                "init buffer with binary data") )
        .def(init<object, string>())
        .def(init<object>())
        .def("__repr__", &Message::Blob::_repr)
        .add_property("mime_type", (string(Message::Blob::*)()) &Message::Blob::mime_type,
                (void(Message::Blob::*)(string)) &Message::Blob::mime_type,
                "MIME type of object in Blob")
        .add_property("filename", (string(Message::Blob::*)()) &Message::Blob::filename,
                (void(Message::Blob::*)(string)) &Message::Blob::filename,
                "filename of object in Blob")
        .add_property("size", &Message::Blob::size, "size of Blob in bytes");

    ((PyTypeObject *)(void *)blob_class.ptr())->tp_as_buffer = &Message::Blob::bp;

    auto message_class = class_<Message>("Message", "p≡p message")
        .def(init<string>())
        .def("__str__", &Message::_str)
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
        .add_property("attachments", (tuple(Message::*)()) &Message::attachments,
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
        .def("encrypt", (Message(Message::*)())&Message::encrypt, "encrypt message")
        .def("encrypt", (Message(Message::*)(list))&Message::encrypt, "encrypt message")
        .def("encrypt", (Message(Message::*)(list,int))&Message::encrypt, "encrypt message")
        .def("encrypt", (Message(Message::*)(list,int,int))&Message::encrypt, "encrypt message")
        .def("decrypt", &Message::decrypt, "decrypt message");

    // basic API

    def("update_identity", &update_identity, "update identity information");
    def("myself", &myself, "ensures that the own identity is being complete");

    // message API

    def("encrypt_message", &encrypt_message, "encrypt message in memory");
    def("decrypt_message", &decrypt_message, "decrypt message in memory");

    // key sync API

    auto sync_mixin_class = class_<SyncMixIn>("SyncMixIn", "p≡p Sync MixIn");

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

