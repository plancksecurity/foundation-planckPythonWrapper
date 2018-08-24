// This file is under GNU Affero General Public License 3.0
// see LICENSE.txt

#pragma once

#include "pEpmodule.hh"
#include <setjmp.h> 
#include <pEp/sync_api.h>

namespace pEp {
    namespace PythonAdapter {

        typedef enum _timeout_state_t {
            timeout_stopped,
            timeout_running,
            timeout_canceling,
            timeout_expiring 
        } timeout_state_t;

        class SyncMixIn {
            public:
                SyncMixIn() { }
                virtual ~SyncMixIn() { }

                virtual void messageToSend(Message msg) {
                    throw runtime_error("override this method");
                }

                virtual void notifyHandshake(
                    pEp::PythonAdapter::Identity me,
                    pEp::PythonAdapter::Identity partner, 
                    sync_handshake_signal signal)
                {
                    throw runtime_error("override this method");
                }

                virtual void deliverHandshakeResult(
                    pEp::PythonAdapter::Identity partner, int result);
#ifndef NDEBUG
                virtual void _inject(
                    int event, 
                    pEp::PythonAdapter::Identity partner, object extra);
#endif
                virtual void setTimeout(time_t timeout){
                    throw runtime_error("override this method");
                }

                virtual time_t cancelTimeout(){
                    throw runtime_error("override this method");
                }

                virtual void onTimeout();

            protected:
                static PEP_STATUS _messageToSend(void *obj, message *msg);
                static PEP_STATUS _notifyHandshake(void *obj,
                        pEp_identity *me, pEp_identity *partner, sync_handshake_signal signal);

                static jmp_buf env;
                static void *_msg;
                static timeout_state_t timeout_state;
                static bool last_turn;
                static time_t remaining_time;
                static int inject_sync_msg(void *msg, void *management);
                static void *retrieve_next_sync_msg(void *management, time_t *timeout);
        };

        class SyncMixIn_callback : public SyncMixIn {
            PyObject* const _self;

            public:
                SyncMixIn_callback(PyObject *self);
                ~SyncMixIn_callback();

                void messageToSend(Message msg);
                void notifyHandshake(
                    pEp::PythonAdapter::Identity me,
                    pEp::PythonAdapter::Identity partner, 
                    sync_handshake_signal signal);

                void setTimeout(time_t timeout);
                time_t cancelTimeout();
        };
    }
}

