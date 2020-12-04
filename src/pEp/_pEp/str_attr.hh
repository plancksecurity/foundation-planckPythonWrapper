// This file is under GNU Affero General Public License 3.0
// see LICENSE.txt

#ifndef STR_ATTR_HH
#define STR_ATTR_HH

#include "adapter_main.hh"

namespace pEp {
namespace PythonAdapter {

bp::object repr(bp::object s);

string repr(const string &s);

string str_attr(char *&str);

void str_attr(char *&str, const string &value);

time_t timestamp_attr(::timestamp *&ts);

void timestamp_attr(::timestamp *&ts, time_t value);

bp::list strlist_attr(::stringlist_t *&sl);

void strlist_attr(::stringlist_t *&sl, bp::list value);

bp::dict strdict_attr(::stringpair_list_t *&spl);

void strdict_attr(::stringpair_list_t *&spl, bp::dict value);

::stringlist_t *to_stringlist(bp::list l);

bp::list from_stringlist(const ::stringlist_t *sl);

} /* namespace PythonAdapter */
} /* namespace pEp */

#endif /* STR_ATTR_HH */
