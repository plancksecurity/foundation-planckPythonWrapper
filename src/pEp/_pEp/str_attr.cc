// This file is under GNU Affero General Public License 3.0
// see LICENSE.txt

// System
#include <cstdlib>
#include <boost/python.hpp>
#include <boost/locale.hpp>

// local
#include "str_attr.hh"

namespace pEp {
namespace PythonAdapter {
using namespace std;
namespace bp = boost::python;
namespace bl = boost::locale;

bp::object repr(bp::object s) {
    return s.attr("__repr__")();
}

string repr(string s) {
    bp::str _s = s.c_str();
    bp::object _r = _s.attr("__repr__")();
    string r = bp::extract<string>(_r);
    return r;
}

string str_attr(char *&str) {
    if (!str) {
        return string("");
    }
    return string(str);
}

void str_attr(char *&str, string value) {
    string normalized = normalize(value, bl::norm_nfc);
    free(str);
    str = strdup(normalized.c_str());
    if (!str) {
        throw bad_alloc();
    }
}

time_t timestamp_attr(::timestamp *&ts) {
    if (!ts) {
        return 0;
    }

    return timegm(ts);
}

void timestamp_attr(::timestamp *&ts, time_t value) {
    free_timestamp(ts);
    ts = ::new_timestamp(value);
}

bp::list strlist_attr(::stringlist_t *&sl) {
    bp::list result;

    for (::stringlist_t *_sl = sl; _sl && _sl->value; _sl = _sl->next) {
        string s(_sl->value);
        result.append(bp::object(s));
    }

    return result;
}

void strlist_attr(::stringlist_t *&sl, bp::list value) {
    ::stringlist_t *_sl = ::new_stringlist(NULL);
    if (!_sl) {
        throw bad_alloc();
    }

    ::stringlist_t *_s = _sl;
    for (int i = 0; i < len(value); i++) {
        bp::extract<string> extract_string(value[i]);
        if (!extract_string.check()) {
            free_stringlist(_sl);
        }
        string s = extract_string();
        s = normalize(s, bl::norm_nfc);
        _s = stringlist_add(_s, s.c_str());
        if (!_s) {
            free_stringlist(_sl);
            throw bad_alloc();
        }
    }

    free_stringlist(sl);
    sl = _sl;
}

bp::dict strdict_attr(::stringpair_list_t *&spl) {
    bp::dict result;

    for (::stringpair_list_t *_spl = spl; _spl && _spl->value; _spl = _spl->next) {
        ::stringpair_t *p = _spl->value;
        if (p->key && p->value) {
            string key(p->key);
            string value(p->value);

            result[key] = value;
        }
    }

    return result;
}

void strdict_attr(::stringpair_list_t *&spl, bp::dict value) {
    ::stringpair_list_t *_spl = ::new_stringpair_list(NULL);
    if (!_spl) {
        throw bad_alloc();
    }

    ::stringpair_list_t *_s = _spl;
    for (int i = 0; i < len(value); i++) {
        bp::extract<string> extract_key(value.keys()[i]);
        bp::extract<string> extract_value(value.values()[i]);

        if (!(extract_key.check() && extract_value.check())) {
            free_stringpair_list(_spl);
        }

        string key = extract_key();
        key = normalize(key, bl::norm_nfc);
        string _value = extract_value();
        _value = normalize(_value, bl::norm_nfc);
        ::stringpair_t *pair = ::new_stringpair(key.c_str(), _value.c_str());
        if (!pair) {
            free_stringpair_list(_spl);
            throw bad_alloc();
        }
        _s = stringpair_list_add(_s, pair);
        if (!_s) {
            free_stringpair_list(_spl);
            throw bad_alloc();
        }
    }

    free_stringpair_list(spl);
    spl = _spl;
}

::stringlist_t *to_stringlist(bp::list l) {
    ::stringlist_t *result = ::new_stringlist(NULL);
    if (!result) {
        throw bad_alloc();
    }

    ::stringlist_t *_s = result;
    for (int i = 0; i < len(l); i++) {
        bp::extract<string> extract_string(l[i]);
        if (!extract_string.check()) {
            free_stringlist(result);
        }
        string s = extract_string();
        _s = stringlist_add(_s, s.c_str());
        if (!_s) {
            free_stringlist(result);
            throw bad_alloc();
        }
    }

    return result;
}

bp::list from_stringlist(const ::stringlist_t *sl) {
    bp::list result;
    for (const ::stringlist_t *_sl = sl; _sl && _sl->value; _sl = _sl->next) {
        string s = _sl->value;
        result.append(s);
    }
    return result;
}

} // namespace PythonAdapter
} // namespace pEp {

