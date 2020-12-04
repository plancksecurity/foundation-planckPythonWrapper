// This file is under GNU Affero General Public License 3.0
// see LICENSE.txt

#ifndef ADAPTER_MAIN_HH
#define ADAPTER_MAIN_HH

// System
#include <string>
#include <iomanip>

// Boost
#include <boost/python.hpp>
#include <boost/locale.hpp>

// Engine
#include <pEp/pEpEngine.h>
#include <pEp/keymanagement.h>
#include <pEp/identity_list.h>
#include <pEp/key_reset.h>
#include <pEp/sync_api.h>
#include <pEp/mime.h>
#include <pEp/message.h>
#include <pEp/message_api.h>
#include <pEp/sync_codec.h>
#include <pEp/distribution_codec.h>
#include <pEp/timestamp.h>
#include <pEp/stringpair.h>

// libpEpAdapter
#include <pEp/Adapter.hh>
#include <pEp/callback_dispatcher.hh>
#include <pEp/status_to_string.hh>
#include <pEp/pEpLog.hh>

namespace pEp {
namespace PythonAdapter {

using namespace std;
namespace bp = boost::python;
namespace bl = boost::locale;

void init_before_main_module();

void _init_after_main_module();

void testfunc();


//extern string device_name;

string about();

void config_passive_mode(bool enable);

void start_sync();

void shutdown_sync();

void debug_color(int ansi_color);

bool is_sync_active();

void config_unencrypted_subject(bool enable);

void key_reset_user(const string &user_id, const string &fpr);

void key_reset_user2(const string &user_id);

void key_reset_all_own_keys();

void _throw_status(::PEP_STATUS status);

void leave_device_group();

::PEP_STATUS _messageToSend(::message *msg);

::PEP_STATUS notifyHandshake(::pEp_identity *me, ::pEp_identity *partner, ::sync_handshake_signal signal);

void deliverHandshakeResult(int result, bp::object identities);

} // namespace PythonAdapter
} // namespace pEp

#endif // ADAPTER_MAIN_HH
