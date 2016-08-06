#pragma once

#include <string>
#include <pEp/pEpEngine.h>
#include <pEp/timestamp.h>

namespace pEp {
    namespace utility {
        using namespace std;
        using namespace boost::python;

        string str_attr(char *&str);
        void str_attr(char *&str, string value);

        time_t timestamp_attr(timestamp *&ts);
        void timestamp_attr(timestamp *&ts, time_t value);
    }
}

