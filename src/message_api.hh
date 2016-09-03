#pragma once

#include "pEpmodule.hh"

namespace pEp {
    namespace PythonAdapter {
        Message encrypt_message(Message src, list extra = list(),
                int enc_format = 4, int flags = 0);
        boost::python::tuple decrypt_message(Message src);
        int _color(int rating);
        void _config_keep_sync_msg(bool enabled);
        string sync_decode(object buffer);
        object sync_encode(string text);
    }
}

