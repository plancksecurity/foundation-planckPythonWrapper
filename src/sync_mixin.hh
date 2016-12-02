#pragma once

#include "pEpmodule.hh"
#include <setjmp.h> 
#include <pEp/sync.h>

namespace pEp {
    namespace PythonAdapter {
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

                virtual void cancelTimeout(){
                    throw runtime_error("override this method");
                }

                virtual void onTimeout();

            protected:
                static PEP_STATUS _messageToSend(void *obj, message *msg);
                static PEP_STATUS _notifyHandshake(void *obj,
                        pEp_identity *me, pEp_identity *partner, sync_handshake_signal signal);

                static jmp_buf env;
                static bool running_timeout;
                static bool expiring_timeout;
                static void *_msg;
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
                void cancelTimeout();
        };
    }
}

