// This file is under GNU Affero General Public License 3.0
// see LICENSE.txt

#ifndef PEPMODULE_HH
#define PEPMODULE_HH

// Engine
#include <pEp/pEpEngine.h>

// local
#include "message.hh"

namespace pEp {
    namespace PythonAdapter {

        extern string device_name;

        void config_passive_mode(bool enable);

        void config_unencrypted_subject(bool enable);

        void key_reset_user(string user_id, string fpr);

        void key_reset_all_own_keys();

        void _throw_status(PEP_STATUS status);

        PEP_STATUS _messageToSend(::message *msg);

        PEP_STATUS _notifyHandshake(pEp_identity *me, pEp_identity *partner, sync_handshake_signal signal);

    } /* namespace PythonAdapter */
} /* namespace pEp */

#endif /* PEPMODULE_HH */
