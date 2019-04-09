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
                bool passive_mode;
                bool unencrypted_subject;

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
                    static ::utility::locked_queue< SYNC_EVENT > q;
                    return q;
                }

                void config_passive_mode(bool enable);
                void config_unencrypted_subject(bool enable);

            protected:
                static PyObject *ui_object(PyObject *value = nullptr);
                static int _inject_sync_event(SYNC_EVENT ev, void *management);

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

