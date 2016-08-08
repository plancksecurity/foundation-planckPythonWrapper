#pragma once

#include "pEpmodule.hh"

namespace pEp {
    namespace PythonAdapter {
        class SyncMixIn {
            public:
                virtual ~SyncMixIn() { }
                void register_for_keysync();

            protected:
                static PEP_STATUS messageToSend(void *obj, const message *msg);
                static PEP_STATUS showHandshake(void *obj,
                        const pEp_identity *self, const pEp_identity *partner);
        };
    }
}

