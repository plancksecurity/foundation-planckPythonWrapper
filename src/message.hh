#pragma once

#include <boost/python.hpp>
#include <pEp/message.h>
#include <string>
#include <list>
#include <vector>
#include <iterator>
#include "str_attr.hh"

namespace pEp {
    namespace PythonAdapter {
        using namespace utility;
        using namespace boost::python;

        // Message is owning a message struct

        class Message {
            message *_msg;

        public:
            // Blob is owning a bloblist_t struct

            class Blob {
                bloblist_t *_bl;
                bool part_of_chain;

            public:
                Blob(bloblist_t *bl = new_bloblist(NULL, 0, NULL, NULL));
                Blob(object data);
                Blob(const Blob& second);
                ~Blob();

                string mime_type() { return _bl ? str_attr(_bl->mime_type) : ""; }
                void mime_type(string value) { str_attr(_bl->mime_type, value); }

                string filename() { return str_attr(_bl->filename); }
                void filename(string value) { str_attr(_bl->filename, value); }

                size_t size() { return _bl->size; }

                static PyBufferProcs bp;

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

            bloblist_t *attachments;
            char *rawmsg_ref;
            size_t rawmsg_size;
            timestamp *sent;
            timestamp *recv;
            pEp_identity *from;
            identity_list *to;
            pEp_identity *recv_by;

            identity_list *cc;
            identity_list *bcc;
            identity_list *reply_to;
            stringlist_t *in_reply_to;

            struct _message *refering_msg_ref;
            stringlist_t *references;
            struct _message_ref_list *refered_by;

            stringlist_t *keywords;
            char *comments;
            stringpair_list_t *opt_fields;
            PEP_enc_format enc_format;
        };
    }
}

