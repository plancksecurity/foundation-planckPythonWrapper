// This file is under GNU Affero General Public License 3.0
// see LICENSE.txt

#include "user_interface.hh"
#include <assert.h>
#include <time.h>

namespace pEp {
    namespace PythonAdapter {
        UserInterface_callback::UserInterface_callback(PyObject *self) :
            _self(self)
        {
            adapter.ui_object(self);
            PEP_STATUS status = ::register_sync_callbacks(adapter.session(),
                    (void *) this, _notifyHandshake, retrieve_next_sync_event);
            assert(status == PEP_STATUS_OK);
            if (status)
                _throw_status(status);
        }

        UserInterface_callback::~UserInterface_callback()
        {
            ::unregister_sync_callbacks(adapter.session());
        }

        PEP_STATUS UserInterface::_notifyHandshake(void *obj,
                pEp_identity *me, pEp_identity *partner,
                sync_handshake_signal signal
            )
        {
            if (!obj)
                return PEP_SEND_FUNCTION_NOT_REGISTERED;

            if (!(me && partner))
                return PEP_ILLEGAL_VALUE;

            auto that = dynamic_cast< UserInterface_callback * >(
                    static_cast< UserInterface * > (obj));
            that->notifyHandshake(Identity(me), Identity(partner), signal);

            return PEP_STATUS_OK;
        }

        void UserInterface::deliverHandshakeResult(Identity partner,
                int result)
        {
            PEP_STATUS status = ::deliverHandshakeResult(adapter.session(),
                    partner, (sync_handshake_result) result);
            _throw_status(status);
        }

        SYNC_EVENT UserInterface::retrieve_next_sync_event(void *management)
        {
            while (adapter.q.empty())
                nanosleep((const struct timespec[]){{0, 100000000L}}, NULL);
            return adapter.q.pop_front();
        }

        void UserInterface_callback::notifyHandshake(
            Identity me, Identity partner, sync_handshake_signal signal)
        {
            call_method< void >(_self, "notifyHandshake", me, partner, signal);
        }
    }
}

