#pragma once

#include "pEpmodule.hh"

namespace pEp {
    namespace PythonAdapter {
        class SyncMixIn {
            public:
                SyncMixIn();
                virtual ~SyncMixIn();

                virtual void messageToSend(Message msg) {
                    throw runtime_error("override this method");
                }

                virtual void showHandshake(Identity me, Identity partner) {
                    throw runtime_error("override this method");
                }

                virtual void deliverHandshakeResult(int result);
#ifndef NDEBUG
                virtual void _inject(int event, Identity *partner, object extra);
#endif

            protected:
                static PEP_STATUS _messageToSend(void *obj, message *msg);
                static PEP_STATUS _showHandshake(void *obj,
                        pEp_identity *me, pEp_identity *partner);
        };

        class SyncMixIn_callback : public SyncMixIn {
            PyObject* const _self;

            public:
                SyncMixIn_callback(PyObject *self) : _self(self) { }

                void _messageToSend(Message msg);
                void _showHandshake(Identity me, Identity partner);
        };
    }
}
