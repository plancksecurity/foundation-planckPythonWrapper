#include "sync_mixin.hh"
#include <pEp/sync.h>
#include <assert.h>

namespace pEp {
    namespace PythonAdapter {
        SyncMixIn::SyncMixIn()
        {
            PEP_STATUS status = register_sync_callbacks(session, (void *) this,
                    _messageToSend, _showHandshake);
            assert(status == PEP_STATUS_OK);
        }

        SyncMixIn::~SyncMixIn() {
            unregister_sync_callbacks(session);
        }

        PEP_STATUS SyncMixIn::_messageToSend(void *obj, message *msg)
        {
            if (!obj)
                return PEP_SEND_FUNCTION_NOT_REGISTERED;

            if (!msg)
                return PEP_ILLEGAL_VALUE;

            auto that = dynamic_cast< SyncMixIn_callback * >(
                    static_cast< SyncMixIn * > (obj));
            that->messageToSend(Message(msg));

            return PEP_STATUS_OK;
        }

        PEP_STATUS SyncMixIn::_showHandshake(void *obj,
                pEp_identity *me, pEp_identity *partner)
        {
            if (!obj)
                return PEP_SEND_FUNCTION_NOT_REGISTERED;

            if (!(me && partner))
                return PEP_ILLEGAL_VALUE;

            auto that = dynamic_cast< SyncMixIn_callback * >(
                    static_cast< SyncMixIn * > (obj));
            that->showHandshake(Identity(me), Identity(partner));

            return PEP_STATUS_OK;
        }

        void SyncMixIn_callback::_messageToSend(Message msg)
        {
            call_method< void >(_self, "messageToSend", msg);
        }

        void SyncMixIn_callback::_showHandshake(Identity me, Identity partner)
        {
            call_method< void >(_self, "showHandshake", me, partner);
        }
    }
}

