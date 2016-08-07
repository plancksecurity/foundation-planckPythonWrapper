#pragma once

#include "pEpmodule.hh"

namespace pEp {
    namespace PythonAdapter {
        Message encrypt_message(Message& src, list extra, int enc_format,
                int flags);
    }
}

