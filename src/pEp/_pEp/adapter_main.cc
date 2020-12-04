// This file is under GNU Affero General Public License 3.0
// see LICENSE.txt

#include "adapter_main.hh"
#include "message.hh"
#include "message_api.hh"

namespace pEp {
namespace PythonAdapter {


static const char *version_string = "p≡p Python adapter version 0.3";

void init_before_main_module() {
    pEpLog("called");
}

// hidden init function, wrapped by hello_world.init()
void _init_after_main_module() {
    pEpLog("called");
    callback_dispatcher.add(_messageToSend, notifyHandshake, nullptr, nullptr);
    Adapter::_messageToSend = CallbackDispatcher::messageToSend;
}

void config_passive_mode(bool enable) {
    ::config_passive_mode(Adapter::session(), enable);
}

void config_unencrypted_subject(bool enable) {
    ::config_unencrypted_subject(Adapter::session(), enable);
}

void key_reset_user(const string &user_id, const string &fpr) {
    if (user_id == "") {
        throw invalid_argument("user_id required");
    }

    ::PEP_STATUS status = ::key_reset_user(Adapter::session(), user_id.c_str(), fpr != "" ? fpr.c_str() : nullptr);
    _throw_status(status);
}

void key_reset_user2(const string &user_id) {
    key_reset_user(user_id, "");
}

void key_reset_all_own_keys() {
    ::PEP_STATUS status = ::key_reset_all_own_keys(Adapter::session());
    _throw_status(status);
}

string about() {
    string version = string(version_string) + "\np≡p version " + PEP_VERSION + "\n";
    return version;
}

void _throw_status(::PEP_STATUS status) {
    if (status == ::PEP_STATUS_OK) {
        return;
    }
    if (status >= 0x400 && status <= 0x4ff) {
        return;
    }
    if (status == ::PEP_OUT_OF_MEMORY) {
        throw bad_alloc();
    }
    if (status == ::PEP_ILLEGAL_VALUE) {
        throw invalid_argument("illegal value");
    }

    if (status_to_string(status) == "unknown status code") {
        stringstream build;
        build << setfill('0') << "p≡p 0x" << setw(4) << hex << status;
        throw runtime_error(build.str());
    } else {
        throw runtime_error(status_to_string(status));
    }
}

::PEP_STATUS _messageToSend(::message *msg) {
    pEpLog("called");
    try {
        PyGILState_STATE gil = PyGILState_Ensure();
        pEpLog("GIL Aquired");
        bp::object modref = bp::import("pEp");
        bp::object funcref = modref.attr("message_to_send");
        bp::call<void>(funcref.ptr(), Message());
        PyGILState_Release(gil);
        pEpLog("GIL released");
    } catch (exception &e) {
    }

    return ::PEP_STATUS_OK;
}

::PEP_STATUS notifyHandshake(::pEp_identity *me, ::pEp_identity *partner, ::sync_handshake_signal signal) {
    pEpLog("called");
    try {
        PyGILState_STATE gil = PyGILState_Ensure();
        pEpLog("GIL Aquired");
        bp::object modref = bp::import("pEp");
        bp::object funcref = modref.attr("notify_handshake");
        bp::call<void>(funcref.ptr(), me, partner, signal);
        PyGILState_Release(gil);
        pEpLog("GIL released");
    } catch (exception &e) {
    }

    return ::PEP_STATUS_OK;
}

void start_sync() {
    CallbackDispatcher::start_sync();
}

void shutdown_sync() {
    CallbackDispatcher::stop_sync();
}

void debug_color(int ansi_color) {
    ::set_debug_color(Adapter::session(), ansi_color);
}

void leave_device_group() {
    ::leave_device_group(Adapter::session());
}

bool is_sync_active() {
    return Adapter::is_sync_running();
}

void testfunc() {
    _messageToSend(nullptr);
}

void deliverHandshakeResult(int result, bp::object identities) {
    identity_list *shared_identities = nullptr;
    if (identities != bp::api::object() && boost::python::len(identities)) {
        shared_identities = ::new_identity_list(nullptr);
        if (!shared_identities) {
            throw bad_alloc();
        }

        try {
            ::identity_list *si = shared_identities;
            for (int i = 0; i < bp::len(identities); ++i) {
                Identity ident = bp::extract<Identity>(identities[i]);
                si = ::identity_list_add(si, ident);
                if (!si) {
                    throw bad_alloc();
                }
            }
        } catch (exception &ex) {
            ::free_identity_list(shared_identities);
            throw ex;
        }
    }

    ::PEP_STATUS status = ::deliverHandshakeResult(Adapter::session(), (::sync_handshake_result)result, shared_identities);
    free_identity_list(shared_identities);
    _throw_status(status);
}
} // namespace PythonAdapter
} // namespace pEp
