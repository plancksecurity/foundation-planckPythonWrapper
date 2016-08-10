#pragma once

#include "pEpmodule.hh"

namespace pEp {
    namespace PythonAdapter {
        class SyncMixIn {
            public:
                SyncMixIn();
                virtual ~SyncMixIn();

            protected:
                static PEP_STATUS messageToSend(void *obj, message *msg);
                static PEP_STATUS showHandshake(void *obj,
                        pEp_identity *self, pEp_identity *partner);
        };
    }
}

