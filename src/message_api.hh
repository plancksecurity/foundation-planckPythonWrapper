// This file is under GNU Affero General Public License 3.0
// see LICENSE.txt

#pragma once

#include "pEpmodule.hh"

namespace pEp {
    namespace PythonAdapter {
        Message encrypt_message(Message src, boost::python::list extra = boost::python::list(),
                int enc_format = 4, int flags = 0);
        boost::python::tuple decrypt_message(Message src, int flags=0);
        int _color(int rating);
        object sync_search(string name);
    }
}

