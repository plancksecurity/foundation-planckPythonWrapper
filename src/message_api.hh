#pragma once

#include "pEpmodule.hh"

namespace pEp {
    namespace PythonAdapter {
        Message encrypt_message(Message src, boost::python::list extra = boost::python::list(),
                int enc_format = 4, int flags = 0);
        boost::python::tuple decrypt_message(Message src);
        int _color(int rating);
        void _config_keep_sync_msg(bool enabled);
        object sync_search(string name);
    }
}

