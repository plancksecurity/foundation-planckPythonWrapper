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

        object repr(object s);
        string repr(string s);

        string str_attr(char *&str);
        void str_attr(char *&str, string value);

        time_t timestamp_attr(timestamp *&ts);
        void timestamp_attr(timestamp *&ts, time_t value);

        boost::python::list strlist_attr(stringlist_t *&sl);
        void strlist_attr(stringlist_t *&sl, boost::python::list value);

        dict strdict_attr(stringpair_list_t *&spl);
        void strdict_attr(stringpair_list_t *&spl, dict value);

        stringlist_t *to_stringlist(boost::python::list l);
        boost::python::list from_stringlist(const stringlist_t *sl);
    }
}

