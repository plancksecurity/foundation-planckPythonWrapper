#pragma once

#include <boost/python.hpp>
#include <pEp/message.h>
#include <string>
#include "Identity.hh"
#include "str_attr.hh"

namespace pEp {
    namespace PythonAdapter {
        using namespace utility;
        using namespace boost::python;

        // Message is owning a message struct

        class Message {
            message *_msg;

        public:
            // Blob is owning a bloblist_t struct - or not and just managing
            // one depending on part_of_chain

            class Blob {
                bloblist_t *_bl;
                bool part_of_chain;

            public:
                Blob(bloblist_t *bl = new_bloblist(NULL, 0, NULL, NULL),
                        bool chained = false);
                Blob(object data, string mime_type, string filename);
                Blob(const Blob& second);
                ~Blob();

                string mime_type() { return _bl ? str_attr(_bl->mime_type) : ""; }
                void mime_type(string value) { str_attr(_bl->mime_type, value); }

                string filename() { return str_attr(_bl->filename); }
                void filename(string value) { str_attr(_bl->filename, value); }

                size_t size() { return _bl->size; }

                static PyBufferProcs bp;

                friend class Message;

            protected:
                static int getbuffer(PyObject *self, Py_buffer *view, int flags);
            };

            Message(PEP_msg_direction dir = PEP_dir_outgoing);
            Message(const Message& second);
            Message(message *ident);
            ~Message();
            operator message *();
            void attach(message *ident);
            message *detach();

            PEP_msg_direction dir() { return _msg->dir; }
            void dir(PEP_msg_direction value) { _msg->dir = value; }

            string id() { return str_attr(_msg->id); }
            void id(string value) { str_attr(_msg->id, value); }

            string shortmsg() { return str_attr(_msg->shortmsg); }
            void shortmsg(string value) { str_attr(_msg->shortmsg, value); }

            string longmsg() { return str_attr(_msg->longmsg); }
            void longmsg(string value) { str_attr(_msg->longmsg, value); }

            string longmsg_formatted() { return str_attr(_msg->longmsg_formatted); }
            void longmsg_formatted(string value) { str_attr(_msg->longmsg_formatted, value); }

            tuple attachments();
            void attachments(list value);

            time_t sent() { return timestamp_attr(_msg->sent); }
            void sent(time_t value) { timestamp_attr(_msg->sent, value); }

            time_t recv() { return timestamp_attr(_msg->recv); }
            void recv(time_t value) { timestamp_attr(_msg->recv, value); }

            object from() { return identity_attr(_msg->from); }
            void from(object value) { identity_attr(_msg->from, value); }

            list to() { return identitylist_attr(_msg->to); }
            void to(list value) { identitylist_attr(_msg->to, value); }

            object recv_by() { return identity_attr(_msg->recv_by); }
            void recv_by(object value) { identity_attr(_msg->recv_by, value); }

            list cc() { return identitylist_attr(_msg->cc); }
            void cc(list value) { identitylist_attr(_msg->cc, value); }

            list bcc() { return identitylist_attr(_msg->bcc); }
            void bcc(list value) { identitylist_attr(_msg->bcc, value); }

            list reply_to() { return identitylist_attr(_msg->reply_to); }
            void reply_to(list value) { identitylist_attr(_msg->reply_to, value); }

            list in_reply_to() { return strlist_attr(_msg->in_reply_to); }
            void in_reply_to(list value) { strlist_attr(_msg->in_reply_to, value); }

            list references() { return strlist_attr(_msg->references); }
            void references(list value) { strlist_attr(_msg->references, value); }

            stringlist_t *keywords;
            char *comments;
            stringpair_list_t *opt_fields;
            PEP_enc_format enc_format;
        };
    }
}

