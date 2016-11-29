#include "sync_mixin.hh"
#include <pEp/sync.h>
#ifndef NDEBUG
#include <pEp/sync_fsm.h>
#endif
#include <assert.h>

namespace pEp {
    namespace PythonAdapter {
        SyncMixIn_callback::SyncMixIn_callback(PyObject *self) : _self(self)
        {
            PEP_STATUS status = register_sync_callbacks(session, (void *) this,
                    _messageToSend, _showHandshake, inject_sync_msg,
                    retrieve_next_sync_msg);
            assert(status == PEP_STATUS_OK);
        }

        SyncMixIn_callback::~SyncMixIn_callback()
        {
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

        void SyncMixIn::deliverHandshakeResult(Identity partner, int result)
        {
            PEP_STATUS status = ::deliverHandshakeResult(session, partner, 
                    (sync_handshake_result) result);
            _throw_status(status);
        }

#ifndef NDEBUG
        void SyncMixIn::_inject(int event, Identity partner, object extra)
        {
            time_t timeout = 0;
            PEP_STATUS status = fsm_DeviceState_inject(session,
                    (DeviceState_event) event, partner, NULL, &timeout);
            _throw_status(status);
        }
#endif

        jmp_buf SyncMixIn::env;
        jmp_buf SyncMixIn::env_timeout;
        void *SyncMixIn::_msg;
        bool SyncMixIn::running_timeout = false;

        int SyncMixIn::inject_sync_msg(void *msg, void *management)
        {
            _msg = msg;
            int val = setjmp(env);
            if (!val){
                if(running_timeout){
                    // call python timeout timer cancel
                    auto that = dynamic_cast< SyncMixIn_callback * >(
                            static_cast< SyncMixIn * > (management));
                    that->cancelTimeout();
                    running_timeout = false;
                }
                do_sync_protocol(session, management);
            }
            return 0;
        }

        void *SyncMixIn::retrieve_next_sync_msg(void *management, time_t *timeout)
        {
            static int twice = 1;
            twice = !twice;
            if (!twice)
                return (void *) _msg;
            if (*timeout != 0){
                int val = setjmp(env_timeout);
                if (!val){
                    // call python timeout timer start
                    auto that = dynamic_cast< SyncMixIn_callback * >(
                            static_cast< SyncMixIn * > (management));
                    that->setTimeout(*timeout);
                    running_timeout = true;
                }else{
                    running_timeout = false;
                    // this will inject tiemout event
                    return NULL;
                }
            }
            longjmp(env, 1);
            return (void *) 23;
        }

        // to be called from python timeout timer - may GIL protect us
        void SyncMixIn::onTimeout(){
            longjmp(env_timeout, 1);
        }

        void SyncMixIn_callback::messageToSend(Message msg)
        {
            call_method< void >(_self, "messageToSend", msg);
        }

        void SyncMixIn_callback::showHandshake(Identity me, Identity partner)
        {
            call_method< void >(_self, "showHandshake", me, partner);
        }

        void SyncMixIn_callback::setTimeout(time_t timeout)
        {
            call_method< void >(_self, "setTimeout", timeout);
        }

        void SyncMixIn_callback::cancelTimeout()
        {
            call_method< void >(_self, "cancelTimeout");
        }
    }
}

