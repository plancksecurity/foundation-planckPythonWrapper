#pragma once

#include <boost/python.hpp>
#include "identity.hh"
#include "message.hh"
#include "adapter.hh"
#include <pEp/pEpEngine.h>

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
        void do_sync_protocol();
        extern Adapter adapter;
    }
}

