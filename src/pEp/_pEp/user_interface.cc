// This file is under GNU Affero General Public License 3.0
// see LICENSE.txt

// System
#include <cassert>

// local
#include "user_interface.hh"

namespace pEp {
    namespace PythonAdapter {
        using namespace std;
        using namespace boost::python;

        UserInterface *UserInterface::_ui = nullptr;

        UserInterface::UserInterface() {
            if (_ui)
                throw runtime_error("only one UserInterface thread allowed");
            _ui = this;
        }

        UserInterface::~UserInterface() {
            _ui = nullptr;
        }

        UserInterface_callback::UserInterface_callback(PyObject *self) :
                UserInterface(), _self(self) {
//    adapter.ui_object(self);
//    ::PEP_STATUS status = ::register_sync_callbacks(Adapter::session(),
//            (void *) this, _notifyHandshake, retrieve_next_sync_event);
//    assert(status == ::PEP_STATUS_OK);
//    if (status)
//        _throw_status(status);
        }

        UserInterface_callback::~UserInterface_callback() {
//    ::unregister_sync_callbacks(Adapter::session());
        }

        ::PEP_STATUS UserInterface::_notifyHandshake(
                pEp_identity *me, pEp_identity *partner,
                sync_handshake_signal signal
        ) {
            if (!(me && partner))
                return PEP_ILLEGAL_VALUE;

            auto that = dynamic_cast< UserInterface_callback * >(_ui);
            that->notifyHandshake(Identity(me), Identity(partner), signal);

            return ::PEP_STATUS_OK;
        }

        void UserInterface::deliverHandshakeResult(int result, object identities) {
            identity_list *shared_identities = nullptr;
            if (identities != boost::python::api::object() && boost::python::len(identities)) {
                shared_identities = new_identity_list(nullptr);
                if (!shared_identities)
                    throw bad_alloc();

                try {
                    identity_list *si = shared_identities;
                    for (int i = 0; i < boost::python::len(identities); ++i) {
                        Identity ident = extract<Identity>(identities[i]);
                        si = identity_list_add(si, ident);
                        if (!si)
                            throw bad_alloc();
                    }
                }
                catch (exception &ex) {
                    free_identity_list(shared_identities);
                    throw ex;
                }
            }

            ::PEP_STATUS status = ::deliverHandshakeResult(Adapter::session(),
                                                         (sync_handshake_result) result, shared_identities);
            free_identity_list(shared_identities);
            _throw_status(status);
        }

//PEP_rating UserInterface::get_key_rating_for_user(string user_id, string fpr)
//{
//    PEP_rating result;
//    ::PEP_STATUS status =
//        ::get_key_rating_for_user(Adapter::session(),
//                user_id.c_str(), fpr.c_str(), &result);
//    _throw_status(status);
//    return result;
//}

//SYNC_EVENT UserInterface::retrieve_next_sync_event(void *management, unsigned threshold)
//{
//    time_t started = time(nullptr);
//    bool timeout = false;
//
//    while (adapter.queue().empty()) {
//        int i = 0;
//        ++i;
//        if (i > 10) {
//            if (time(nullptr) > started + threshold) {
//                timeout = true;
//                break;
//            }
//            i = 0;
//        }
//        nanosleep((const struct timespec[]){{0, 100000000L}}, NULL);
//    }
//
//    if (timeout)
//        return new_sync_timeout_event();
//
//    return adapter.queue().pop_front();
//}

        void UserInterface_callback::notifyHandshake(
                Identity me, Identity partner, sync_handshake_signal signal) {
            call_method<void>(_self, "notifyHandshake", me, partner, signal);
        }

    } // namespace PythonAdapter
} // namespace pEp {

