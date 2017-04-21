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
                    _messageToSend, _notifyHandshake, inject_sync_msg,
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

        PEP_STATUS SyncMixIn::_notifyHandshake(void *obj,
                pEp_identity *me, pEp_identity *partner, sync_handshake_signal signal)
        {
            if (!obj)
                return PEP_SEND_FUNCTION_NOT_REGISTERED;

            if (!(me && partner))
                return PEP_ILLEGAL_VALUE;

            auto that = dynamic_cast< SyncMixIn_callback * >(
                    static_cast< SyncMixIn * > (obj));
            that->notifyHandshake(Identity(me), Identity(partner), signal);

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
        void *SyncMixIn::_msg;

        timeout_state_t SyncMixIn::timeout_state = timeout_stopped;
        bool SyncMixIn::last_turn = false;
        time_t SyncMixIn::remaining_time = 0;

        int SyncMixIn::inject_sync_msg(void *msg, void *management)
        {
            assert(timeout_state != timeout_canceling);
            if(timeout_state == timeout_canceling) return 0;

            assert(timeout_state != timeout_expiring);
            if(timeout_state == timeout_expiring) return 0;

            _msg = msg;
            int val = setjmp(env);
            if (!val){
                if(timeout_state == timeout_running){
                    // call python timeout timer cancel
                    auto that = dynamic_cast< SyncMixIn_callback * >(
                            static_cast< SyncMixIn * > (management));
                    remaining_time = that->cancelTimeout();
                    timeout_state = timeout_canceling;
                }
                last_turn = false;
                do_sync_protocol(session, management);
            }
            return 0;
        }

        void *SyncMixIn::retrieve_next_sync_msg(void *management, time_t *timeout)
        {
            if (!last_turn){
                
                assert(timeout_state != timeout_running);
                if(timeout_state == timeout_running) return NULL;

                switch(timeout_state){
                  case timeout_canceling :
                    *timeout = remaining_time;
                    break;
                  case timeout_expiring :
                    // "1" is arbitrary value !=0, since we don't
                    // have original timeout value anymore
                    *timeout = 1;
                    break;
                }

                timeout_state = timeout_stopped;

                last_turn = true;
                return (void *) _msg;

            } else {

                assert(timeout_state == timeout_stopped);
                if(timeout_state != timeout_stopped) return NULL;

                if (*timeout != 0) {
                    // call python timeout timer start
                    auto that = dynamic_cast< SyncMixIn_callback * >(
                            static_cast< SyncMixIn * > (management));
                    that->setTimeout(*timeout);
                    timeout_state = timeout_running;
                }
            }
            longjmp(env, 1);
            return (void *) 23;
        }

        // to be called from python timeout timer - may GIL protect us
        void SyncMixIn::onTimeout(){
            assert(timeout_state != timeout_canceling);
            if(timeout_state == timeout_canceling) return;

            assert(timeout_state != timeout_expiring);
            if(timeout_state == timeout_expiring) return;

            _msg = NULL;
            int val = setjmp(env);
            if (!val){
                timeout_state = timeout_expiring;

                last_turn = false;
                do_sync_protocol(session, (void*)this);
            }
        }

        void SyncMixIn_callback::messageToSend(Message msg)
        {
            call_method< void >(_self, "messageToSend", msg);
        }

        void SyncMixIn_callback::notifyHandshake(
            Identity me, Identity partner, sync_handshake_signal signal)
        {
            call_method< void >(_self, "notifyHandshake", me, partner, signal);
        }

        void SyncMixIn_callback::setTimeout(time_t timeout)
        {
            call_method< void >(_self, "setTimeout", timeout);
        }

        time_t SyncMixIn_callback::cancelTimeout()
        {
            return call_method< time_t >(_self, "cancelTimeout");
        }
    }
}

