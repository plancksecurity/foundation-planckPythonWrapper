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

                virtual void messageToSend(Message msg) {
                    throw runtime_error("override this method");
                }

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

            protected:
                static PyObject *ui_object(PyObject *value = nullptr);
                static PEP_STATUS _messageToSend(struct _message *msg);
                static int _inject_sync_event(SYNC_EVENT ev, void *management);

            private:
                static mutex& mtx()
                {
                    static mutex m;
                    return m;
                }

            friend class UserInterface_callback;
        };

        class Adapter_callback : public Adapter {
            PyObject *_self;
            public:
                Adapter_callback(PyObject *self) : _self(self) { }
                ~Adapter_callback() { }

                void messageToSend(Message msg);

                // non copyable
                Adapter_callback(const Adapter_callback&) = delete;
                Adapter_callback& operator= (const Adapter_callback&) = delete;
        };
    }
}

