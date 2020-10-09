// This file is under GNU Affero General Public License 3.0
// see LICENSE.txt

#ifndef USER_INTERFACE_HH
#define USER_INTERFACE_HH

// System
#include <csetjmp>

// Engine
#include <pEp/sync_api.h>
#include <pEp/message_api.h>

// local
#include "pEpmodule.hh"


namespace pEp {
    namespace PythonAdapter {

        class UserInterface {
            static UserInterface *_ui;
        public:
            UserInterface();

            virtual ~UserInterface();

            virtual void notifyHandshake(
                    Identity me,
                    Identity partner,
                    sync_handshake_signal signal) {
                throw runtime_error("override this method");
            }

            virtual void deliverHandshakeResult(int result, object identities);

//     PEP_rating get_key_rating_for_user(string user_id, string fpr);

        protected:
            static PEP_STATUS _notifyHandshake(pEp_identity *me, pEp_identity *partner, sync_handshake_signal signal);
        };

        class UserInterface_callback : public UserInterface {
            PyObject *_self;
        public:
            UserInterface_callback(PyObject *self);

            ~UserInterface_callback();

            void notifyHandshake(
                    Identity me,
                    Identity partner,
                    sync_handshake_signal signal
            );
        };

    } /* namespace PythonAdapter */
} /* namespace pEp */

#endif /* USER_INTERFACE_HH */

