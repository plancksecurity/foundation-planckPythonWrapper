#pragma once

#include <pEp/pEpEngine.h>
#include "message.hh"

namespace pEp {
    namespace PythonAdapter {
        extern string device_name;
        void config_passive_mode(bool enable);
        void config_unencrypted_subject(bool enable);
        void key_reset_user(string user_id, string fpr);
        void key_reset_all_own_keys();
        void _throw_status(PEP_STATUS status);
        void messageToSend(Message msg);
        PEP_STATUS _messageToSend(::message *msg);
        PEP_STATUS _ensure_passphrase(PEP_SESSION session, const char *fpr);
//         void do_sync_protocol();
//         extern Adapter adapter;
    }
}

