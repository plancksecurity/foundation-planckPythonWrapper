#include "sync_mixin.hh"
#include <pEp/sync.h>
#include <assert.h>

namespace pEp {
    namespace PythonAdapter {
        SyncMixIn::SyncMixIn()
        {
            PEP_STATUS status = register_sync_callbacks(session, (void *) this,
                    messageToSend, showHandshake);
            assert(status == PEP_STATUS_OK);
        }

        SyncMixIn::~SyncMixIn() {
            unregister_sync_callbacks(session);
        }

        PEP_STATUS SyncMixIn::messageToSend(void *obj, const message *msg)
        {
            SyncMixIn *that = (SyncMixIn *) obj;

            return PEP_STATUS_OK;
        }

        PEP_STATUS SyncMixIn::showHandshake(void *obj,
                const pEp_identity *self, const pEp_identity *partner)
        {
            SyncMixIn *that = (SyncMixIn *) obj;

            return PEP_STATUS_OK;
        }
    }
}

