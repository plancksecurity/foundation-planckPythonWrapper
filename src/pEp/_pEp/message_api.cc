// This file is under GNU Affero General Public License 3.0
// see LICENSE.txt

// local
#include "message_api.hh"

namespace pEp {
namespace PythonAdapter {


Message encrypt_message(Message src, bp::list extra, int enc_format, int flags) {
    Identity _from = src.from();
    if (_from.address() == "") {
        throw invalid_argument("encrypt_message: src.from_.address empty");
    }
    if (_from.username() == "") {
        throw invalid_argument("encrypt_message: src.from_.username empty");
    }

    if (_from.user_id() == "") {
        src.from().user_id(_from.address());
    }

    ::stringlist_t *_extra = to_stringlist(extra);
    ::PEP_enc_format _enc_format = (::PEP_enc_format)enc_format;
    ::PEP_encrypt_flags_t _flags = (::PEP_encrypt_flags_t)flags;
    ::message *_dst = nullptr;

    ::message *_src = src;
    ::PEP_STATUS status = ::encrypt_message(Adapter::session(), _src, _extra, &_dst, _enc_format, _flags);
    ::free_stringlist(_extra);
    _throw_status(status);

    if (!_dst || _dst == _src) {
        return Message(_src);
    }

    return Message(_dst);
}

bp::tuple decrypt_message(Message src, int flags) {
    ::message *_dst = nullptr;
    ::stringlist_t *_keylist = nullptr;
    ::PEP_rating _rating = ::PEP_rating_undefined;
    ::PEP_decrypt_flags_t _flags = (::PEP_decrypt_flags_t)flags;
    ::message *_src = src;

    ::PEP_STATUS status = ::decrypt_message(Adapter::session(), _src, &_dst, &_keylist, &_rating, &_flags);
    _throw_status(status);

    bp::list keylist;
    if (_keylist) {
        keylist = from_stringlist(_keylist);
        ::free_stringlist(_keylist);
    }

    Message dst = _dst ? Message(_dst) : Message(src);
    return bp::make_tuple(dst, keylist, _rating, _flags);
}

::PEP_color _color(int rating) {
    return ::color_from_rating((::PEP_rating)rating);
}

bp::tuple sync_decode(bp::object buffer) {
    Py_buffer src;
    int result = PyObject_GetBuffer(buffer.ptr(), &src, PyBUF_CONTIG_RO);
    if (result) {
        throw invalid_argument("need a contiguous buffer to read");
    }

    char *dst = nullptr;
    ::PEP_STATUS status = ::PER_to_XER_Sync_msg((char *)src.buf, src.len, &dst);
    PyBuffer_Release(&src);
    _throw_status(status);

    string _dst(dst);
    free(dst);
    return bp::make_tuple(_dst, 0);
}

static bp::tuple sync_encode(string text) {
    char *data = nullptr;
    size_t size = 0;
    ::PEP_STATUS status = ::XER_to_PER_Sync_msg(text.c_str(), &data, &size);
    _throw_status(status);

    PyObject * ba = PyBytes_FromStringAndSize(data, size);
    free(data);
    if (!ba) {
        throw bad_alloc();
    }

    return bp::make_tuple(bp::object(bp::handle<>(ba)), 0);
}

bp::tuple Distribution_decode(bp::object buffer) {
    Py_buffer src;
    int result = PyObject_GetBuffer(buffer.ptr(), &src, PyBUF_CONTIG_RO);
    if (result) {
        throw invalid_argument("need a contiguous buffer to read");
    }

    char *dst = nullptr;
    ::PEP_STATUS status = ::PER_to_XER_Distribution_msg((char *)src.buf, src.len, &dst);
    PyBuffer_Release(&src);
    _throw_status(status);

    string _dst(dst);
    free(dst);
    return bp::make_tuple(_dst, 0);
}

static bp::tuple Distribution_encode(string text) {
    char *data = nullptr;
    size_t size = 0;
    ::PEP_STATUS status = ::XER_to_PER_Distribution_msg(text.c_str(), &data, &size);
    _throw_status(status);

    PyObject * ba = PyBytes_FromStringAndSize(data, size);
    free(data);
    if (!ba) {
        throw bad_alloc();
    }

    return bp::make_tuple(bp::object(bp::handle<>(ba)), 0);
}

bp::object sync_search(string name) {
    if (name != "pep.sync") {
        return bp::object();
    } else {
        bp::object codecs = bp::import("codecs");
        bp::object CodecInfo = codecs.attr("CodecInfo");

        bp::object _sync_decode = make_function(sync_decode);
        bp::object _sync_encode = make_function(sync_encode);

        return bp::call<bp::object>(CodecInfo.ptr(), _sync_encode, _sync_decode);
    }
}

bp::object distribution_search(string name) {
    if (name != "pep.distribution") {
        return bp::object();
    } else {
        bp::object codecs = bp::import("codecs");
        bp::object CodecInfo = codecs.attr("CodecInfo");

        bp::object _distribution_decode = make_function(Distribution_decode);
        bp::object _distribution_encode = make_function(Distribution_encode);

        return bp::call<bp::object>(CodecInfo.ptr(), _distribution_encode, _distribution_decode);
    }
}

} // namespace PythonAdapter
} // namespace pEp
