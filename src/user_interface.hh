// This file is under GNU Affero General Public License 3.0
// see LICENSE.txt

#pragma once

#include "pEpmodule.hh"
#include <setjmp.h> 
#include <pEp/sync_api.h>

namespace pEp {
    namespace PythonAdapter {
        class UserInterface {
                static UserInterface *_ui;
            public:
                UserInterface();
                virtual ~UserInterface();

                virtual void notifyHandshake(
                    pEp::PythonAdapter::Identity me,
                    pEp::PythonAdapter::Identity partner, 
                    sync_handshake_signal signal)
                {
                    throw runtime_error("override this method");
                }

                virtual void deliverHandshakeResult(
                    pEp::PythonAdapter::Identity partner, int result);

            protected:
                static PEP_STATUS _notifyHandshake(pEp_identity *me,
                        pEp_identity *partner, sync_handshake_signal signal);
                static SYNC_EVENT retrieve_next_sync_event(void *management, time_t threshold);
        };

        class UserInterface_callback : public UserInterface {
                PyObject *_self;
            public:
                UserInterface_callback(PyObject *self);
                ~UserInterface_callback();

                void notifyHandshake(
                    pEp::PythonAdapter::Identity me,
                    pEp::PythonAdapter::Identity partner, 
                    sync_handshake_signal signal);
        };
    }
}

