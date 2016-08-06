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

        list strlist_attr(stringlist_t *&sl)
        {
            list result;

            for (stringlist_t *_sl = sl; _sl && _sl->value; _sl = _sl->next) {
                string s(_sl->value);
                result.append(object(s));
            }

            return result;
        }

        void strlist_attr(stringlist_t *&sl, list value)
        {
            stringlist_t *_sl = new_stringlist(NULL);
            if (!_sl)
                throw bad_alloc();

            stringlist_t *_s = _sl;
            for (int i=0; i<len(value); i++) {
                extract< string > extract_string(value[i]);
                if (!extract_string.check()) {
                    free_stringlist(_sl);
                }
                string s = extract_string();
                _s = stringlist_add(_s, s.c_str());
                if (!_s) {
                    free_stringlist(_sl);
                    throw bad_alloc();
                }
            }

            free_stringlist(sl);
            sl = _sl;
        }
    }
}

