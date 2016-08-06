#include "pEpmodule.hh"
#include <boost/locale.hpp>
#include <string>
#include <pEp/pEpEngine.h>
#include "Identity.hh"
#include "Message.hh"

namespace pEp {
    namespace PythonAdapter {
        using namespace std;

        static string about()
        {
            string version = string(version_string) + "\np≡p version "
                + PEP_VERSION + "\n";
            return version;
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
        .add_property("mime_type", (string(Message::Blob::*)()) &Message::Blob::mime_type,
                (void(Message::Blob::*)(string)) &Message::Blob::mime_type,
                "MIME type of object in Blob")
        .add_property("filename", (string(Message::Blob::*)()) &Message::Blob::filename,
                (void(Message::Blob::*)(string)) &Message::Blob::filename,
                "filename of object in Blob")
        .add_property("size", &Message::Blob::size, "size of Blob in bytes");

    ((PyTypeObject *)(void *)blob_class.ptr())->tp_as_buffer = &Message::Blob::bp;

    auto message_class = class_<Message>("Message", "p≡p message")
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
        .add_property("from_", (object(Message::*)()) &Message::from,
                (void(Message::*)(object)) &Message::from,
                "identity where message is from")
        .add_property("to", (list(Message::*)()) &Message::to,
                (void(Message::*)(list)) &Message::to,
                "list of identities message is going to")
        .add_property("recv_by", (object(Message::*)()) &Message::recv_by,
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
                "opt_fields of message");
}

