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

        PEP_STATUS SyncMixIn::messageToSend(void *obj, message *msg)
        {
            if (!obj)
                return PEP_SEND_FUNCTION_NOT_REGISTERED;

            if (!msg)
                return PEP_ILLEGAL_VALUE;

            object *that = (object *) obj;
            that->attr("messageToSend")(Message(msg));

            return PEP_STATUS_OK;
        }

        PEP_STATUS SyncMixIn::showHandshake(void *obj,
                pEp_identity *self, pEp_identity *partner)
        {
            if (!obj)
                return PEP_SEND_FUNCTION_NOT_REGISTERED;

            if (!(self && partner))
                return PEP_ILLEGAL_VALUE;

            object *that = (object *) obj;
            that->attr("showHandshake")(Identity(self), Identity(partner));

            return PEP_STATUS_OK;
        }
    }
}

