#pragma once

#include <pEp/message.h>
#include <string>
#include <list>
#include "str_attr.hh"

namespace pEp {
    namespace PythonAdapter {
        using namespace utility;

        class Message {
            class Blob {
                char *_value;
                size_t _size;
                string _mime_type;
                string _filename;

            public:
                Blob(char *value = NULL, size_t size = 0, string mime_type = "",
                        string filename = "");
                Blob(const Blob& second);
                ~Blob();
            };

            message *_msg;

        public:
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

