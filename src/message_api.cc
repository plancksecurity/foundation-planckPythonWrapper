#include "message_api.hh"
#include <pEp/message_api.h>

namespace pEp {
    namespace PythonAdapter {
        Message encrypt_message(Message src, list extra, int enc_format,
                int flags)
        {
            Identity _from = src.from();
            if (_from.address() == "")
                throw invalid_argument("encrypt_message: src.from_.address empty");
            if (_from.username() == "")
                throw invalid_argument("encrypt_message: src.from_.username empty");

            stringlist_t *_extra = to_stringlist(extra);
            PEP_enc_format _enc_format = (PEP_enc_format) enc_format;
            PEP_encrypt_flags_t _flags = (PEP_encrypt_flags_t) flags;
            message *_dst = NULL;

            message *_src = src;
            PEP_STATUS status = encrypt_message(session, _src, _extra, &_dst,
                    _enc_format, _flags);
            free_stringlist(_extra);
            _throw_status(status);

            if (!_dst || _dst == src) {
                Message dst(src);
                return dst;
            }
            
            Message dst(_dst);
            return dst;
        }

        boost::python::tuple decrypt_message(Message src)
        {
            message *_dst = NULL;
            stringlist_t *_keylist = NULL;
            PEP_rating _rating = PEP_rating_undefined;
            PEP_decrypt_flags_t _flags = 0;

            PEP_STATUS status = decrypt_message(session, src, &_dst, &_keylist,
                    &_rating, &_flags);
            _throw_status(status);

            list keylist;
            if (_keylist) {
                keylist = from_stringlist(_keylist);
                free_stringlist(_keylist);
            }

            int rating = (int) _rating;
            int flags = (int) _flags;

            Message dst(_dst);
            return boost::python::make_tuple(dst, keylist, rating, flags);
        }

        int _color(int rating)
        {
            return (int) ::color_from_rating((PEP_rating) rating);
        }
    }
}

