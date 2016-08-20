#include "sync_mixin.hh"
#include <pEp/sync.h>
#ifndef NDEBUG
#include <pEp/sync_fsm.h>
#endif
#include <assert.h>

namespace pEp {
    namespace PythonAdapter {
        SyncMixIn::SyncMixIn()
        {
            PEP_STATUS status = register_sync_callbacks(session, (void *) this,
                    _messageToSend, _showHandshake, inject_sync_msg,
                    retrieve_next_sync_msg);
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

        void SyncMixIn::deliverHandshakeResult(int result)
        {
            PEP_STATUS status = ::deliverHandshakeResult(session,
                    (sync_handshake_result) result);
            _throw_status(status);
        }

#ifndef NDEBUG
        void SyncMixIn::_inject(int event, Identity partner, object extra)
        {
            PEP_STATUS status = fsm_DeviceState_inject(session,
                    (DeviceState_event) event, partner, NULL);
            _throw_status(status);
        }
#endif

        jmp_buf SyncMixIn::env;
        int SyncMixIn::val;
        void *SyncMixIn::_msg;

        int SyncMixIn::inject_sync_msg(void *msg, void *management)
        {
            // SyncMixIn *that = (SyncMixIn *) management;
            val = 0;
            _msg = msg;
            setjmp(env);
            if (!val)
                do_sync_protocol(session, management);
            return 0;
        }

        void *SyncMixIn::retrieve_next_sync_msg(void *management)
        {
            static int twice = 1;
            twice = !twice;
            // SyncMixIn *that = (SyncMixIn *) management;
            if (!twice)
                return (void *) _msg;
            longjmp(env, 1);
            return (void *) 23;
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

