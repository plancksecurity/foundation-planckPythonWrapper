#pragma once

#include <pEp/message.h>
#include <string>
#include "str_attr.hh"

namespace pEp {
    namespace PythonAdapter {
        using namespace utility;

        class Message {
            message *_msg;

        public:
            Message();
            Message(const Message& second);
            Message(message *ident);
            ~Message();
            operator message *();
            void attach(message *ident);
            message *detach();

            PEP_msg_direction dir;
            char *id;
            char *shortmsg;
            char *longmsg;

            char *longmsg_formatted;

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

