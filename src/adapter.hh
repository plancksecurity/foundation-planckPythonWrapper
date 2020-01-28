// This file is under GNU Affero General Public License 3.0
// see LICENSE.txt

#pragma once

#include "pEpmodule.hh"
#include "locked_queue.hh"
#include "user_interface.hh"
#include <pEp/sync_api.h>

namespace pEp {
    namespace PythonAdapter {
        using Message = pEp::PythonAdapter::Message;

        class Adapter {
                bool flag_unregister;

            public:
                Adapter(bool unregister_this = false);
                virtual ~Adapter();

                enum session_action {
                    none = 0,
                    init,
                    release
                };

                PEP_SESSION session(session_action action = none);
                static ::utility::locked_queue< SYNC_EVENT >& queue()
                {
                    if (!q)
                        q = new ::utility::locked_queue< SYNC_EVENT >();
                    return *q;
                }
                void script_is_implementing_sync() { flag_sync_enabled = true; }
                void shutdown_sync();
                bool is_sync_active() { return flag_sync_enabled; }

            protected:
                static PyObject *ui_object(PyObject *value = nullptr);
                static int _inject_sync_event(SYNC_EVENT ev, void *management);

                static ::utility::locked_queue< SYNC_EVENT > *q;
                static bool flag_sync_enabled;

                bool queue_active() { return !!q; }

            private:
                static mutex& mtx()
                {
                    static mutex m;
                    return m;
                }

            friend class UserInterface_callback;
        };
    }
}

