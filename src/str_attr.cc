#include "str_attr.hh"
#include <stdlib.h>

namespace pEp {
    namespace utility {
        using namespace std;

        void str_attr(char *&str, string value)
        {
            free(str);
            str = strdup(value.c_str());
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

