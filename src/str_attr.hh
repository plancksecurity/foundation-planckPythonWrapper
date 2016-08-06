#pragma once

#include <string>
#include <pEp/pEpEngine.h>
#include <pEp/timestamp.h>
#include <pEp/stringlist.h>
#include <pEp/stringpair.h>

namespace pEp {
    namespace utility {
        using namespace std;
        using namespace boost::python;

        string str_attr(char *&str);
        void str_attr(char *&str, string value);

        time_t timestamp_attr(timestamp *&ts);
        void timestamp_attr(timestamp *&ts, time_t value);

        list strlist_attr(stringlist_t *&sl);
        void strlist_attr(stringlist_t *&sl, list value);

        dict strdict_attr(stringpair_list_t *&spl);
        void strdict_attr(stringpair_list_t *&spl, dict value);
    }
}

