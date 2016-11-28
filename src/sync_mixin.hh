#pragma once

#include "pEpmodule.hh"
#include <setjmp.h> 

namespace pEp {
    namespace PythonAdapter {
        class SyncMixIn {
            public:
                SyncMixIn() { }
                virtual ~SyncMixIn() { }

                virtual void messageToSend(Message msg) {
                    throw runtime_error("override this method");
                }

                virtual void showHandshake(Identity me, Identity partner) {
                    throw runtime_error("override this method");
                }

                virtual void deliverHandshakeResult(Identity partner, int result);
#ifndef NDEBUG
                virtual void _inject(int event, Identity partner, object extra);
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
                static PEP_STATUS _showHandshake(void *obj,
                        pEp_identity *me, pEp_identity *partner);

                static jmp_buf env;
                static jmp_buf env_timeout;
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
                void showHandshake(Identity me, Identity partner);
                void setTimeout(time_t timeout);
        };
    }
}

