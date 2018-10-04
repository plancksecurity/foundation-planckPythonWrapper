// This file is under GNU Affero General Public License 3.0
// see LICENSE.txt

#include "user_interface.hh"
#include <assert.h>

namespace pEp {
    namespace PythonAdapter {
        Adapter::Adapter(bool unregister_this)
            : flag_unregister(unregister_this)
        {
            session(init);
        }

        Adapter::~Adapter()
        {
            session(release);
        }

        PEP_SESSION Adapter::session(session_action action)
        {
            lock_guard<mutex> lock(mtx());

            thread_local static PEP_SESSION _session = nullptr;
            thread_local int booked = 0;
            PEP_STATUS status = PEP_STATUS_OK;

            switch (action) {
                case release:
                    if (booked)
                        --booked;
                    if (!booked && _session) {
                        ::release(_session);
                        _session = nullptr;
                    }
                    break;

                case none:
                    if (_session)
                        break;

                case init:
                    ++booked;
                    if (!_session)
                        status = ::init(&_session, _messageToSend, _inject_sync_event);
                    break;

                default:
                    status = PEP_ILLEGAL_VALUE;
            }

            if (status)
                _throw_status(status);

            return _session;
        }

        PyObject *Adapter::ui_object(PyObject *value)
        {
            lock_guard<mutex> lock(mtx());
            static PyObject *obj = nullptr;
            if (value)
                obj = value;
            return obj;
        }

        int Adapter::_inject_sync_event(SYNC_EVENT ev, void *management)
        {
            if (is_sync_thread(adapter.session())) {
                PEP_STATUS status = do_sync_protocol_step(adapter.session(), adapter.ui_object(), ev);
                return status == PEP_STATUS_OK ? 0 : 1;
            }

            try {
                queue().push_front(ev);
            }
            catch (exception&) {
                return 1;
            }
            return 0;
        }
    }
}

