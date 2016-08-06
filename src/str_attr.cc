#include "str_attr.hh"
#include <stdlib.h>
#include <boost/locale.hpp>

namespace pEp {
    namespace utility {
        using namespace std;
        using namespace boost::locale;

        void str_attr(char *&str, string value)
        {
            string normalized = normalize(value, norm_nfc);
            free(str);
            str = strdup(normalized.c_str());
            if (!str)
                throw bad_alloc();
        }

        string str_attr(char *&str)
        {
            if (!str)
                return string("");
            return string(str);
        }
    }
}

