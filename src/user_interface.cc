// This file is under GNU Affero General Public License 3.0
// see LICENSE.txt

#include "user_interface.hh"
#include <assert.h>
#include <time.h>

namespace pEp {
    namespace PythonAdapter {
        UserInterface *UserInterface::_ui = nullptr;
        
        UserInterface::UserInterface()
        {
            if (_ui)
                throw runtime_error("only one UserInterface thread allowed");
            _ui = this;
        }

        UserInterface::~UserInterface()
        {
            _ui = nullptr;
        }

        UserInterface_callback::UserInterface_callback(PyObject *self) :
            UserInterface(), _self(self)
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

        PEP_STATUS UserInterface::_notifyHandshake(
                pEp_identity *me, pEp_identity *partner,
                sync_handshake_signal signal
            )
        {
            if (!(me && partner))
                return PEP_ILLEGAL_VALUE;

            auto that = dynamic_cast< UserInterface_callback * >(_ui);
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

        PEP_rating UserInterface::get_key_rating_for_user(string user_id, string fpr)
        {
            PEP_rating result;
            PEP_STATUS status =
                ::get_key_rating_for_user(adapter.session(),
                        user_id.c_str(), fpr.c_str(), &result);
            _throw_status(status);
            return result;
        }

        SYNC_EVENT UserInterface::retrieve_next_sync_event(void *management, unsigned threshold)
        {
            time_t started = time(nullptr);
            bool timeout = false;

            while (adapter.queue().empty()) {
                int i = 0;
                ++i;
                if (i > 10) {
                    if (time(nullptr) > started + threshold) {
                        timeout = true;
                        break;
                    }
                    i = 0;
                }
                nanosleep((const struct timespec[]){{0, 100000000L}}, NULL);
            }

            if (timeout)
                return new_sync_timeout_event();

            return adapter.queue().pop_front();
        }

        void UserInterface_callback::notifyHandshake(
            Identity me, Identity partner, sync_handshake_signal signal)
        {
            call_method< void >(_self, "notifyHandshake", me, partner, signal);
        }
    }
}

