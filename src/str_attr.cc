#include <boost/python.hpp>
#include <boost/locale.hpp>
#include "str_attr.hh"
#include <stdlib.h>

namespace pEp {
    namespace utility {
        using namespace std;
        using namespace boost::locale;

        string str_attr(char *&str)
        {
            if (!str)
                return string("");
            return string(str);
        }

        void str_attr(char *&str, string value)
        {
            string normalized = normalize(value, norm_nfc);
            free(str);
            str = strdup(normalized.c_str());
            if (!str)
                throw bad_alloc();
        }

        time_t timestamp_attr(timestamp *&ts)
        {
            if (!ts)
                return 0;

            return timegm(ts);
        }

        void timestamp_attr(timestamp *&ts, time_t value)
        {
            free_timestamp(ts);
            ts = new_timestamp(value);
        }
    }
}

