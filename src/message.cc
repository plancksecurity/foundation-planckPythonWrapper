// This file is under GNU Affero General Public License 3.0
// see LICENSE.txt

#include <Python.h>
#include "message.hh"
#include "message_api.hh"
#include <stdlib.h>
#include <string.h>
#include <stdexcept>
#include <sstream>
#include <vector>
#include <pEp/mime.h>
#include <pEp/keymanagement.h>
#include <pEp/message_api.h>

namespace pEp {
    namespace PythonAdapter {
        using namespace std;

        Message::Blob::Blob(bloblist_t *bl, bool chained) :
            _bl(bl), part_of_chain(chained)
        {
            if (!_bl)
                throw bad_alloc();
        }

        Message::Blob::Blob(object data, string mime_type, string filename) :
            _bl(new_bloblist(NULL, 0, NULL, NULL)), part_of_chain(false)
        {
            if (!_bl)
                throw bad_alloc();

            Py_buffer src;
            int result = PyObject_GetBuffer(data.ptr(), &src, PyBUF_CONTIG_RO);
            if (result)
                throw invalid_argument("need a contiguous buffer to read");

            char *mem = (char *)malloc(src.len);
            if (!mem) {
                PyBuffer_Release(&src);
                throw bad_alloc();
            }

            memcpy(mem, src.buf, src.len);
            free(_bl->value);
            _bl->size = src.len;
            _bl->value = mem;

            PyBuffer_Release(&src);

            this->mime_type(mime_type);
            this->filename(filename);
        }

        Message::Blob::Blob(const Message::Blob& second) :
            _bl(second._bl), part_of_chain(true)
        {

        }

        Message::Blob::~Blob()
        {
            if (!part_of_chain) {
                free(_bl->value);
                free(_bl);
            }
        }

        string Message::Blob::_repr()
        {
            stringstream build;
            build << "Blob(";
            if (!_bl) {
                build << "b'', '', ''";
            }
            else {
                build << "bytes(" << _bl->size << "), ";
                string mime_type;
                if (_bl->mime_type)
                    mime_type = string(_bl->mime_type);
                string filename;
                if (_bl->filename)
                    filename = string(_bl->filename);
                build << repr(mime_type) << ", ";
                build << repr(filename);
            }
            build << ")";
            return build.str();
        }

        int Message::Blob::getbuffer(PyObject *self, Py_buffer *view, int flags) {
            bloblist_t *bl = NULL;

            try {
                Message::Blob& blob = extract< Message::Blob& >(self);
                bl = blob._bl;
            }
            catch (exception& e) {
                PyErr_SetString(PyExc_RuntimeError, "extract not possible");
                view->obj = NULL;
                return -1;
            }

            if (!(bl && bl->value)) {
                PyErr_SetString(PyExc_RuntimeError, "no data available");
                view->obj = NULL;
                return -1;
            }

            return PyBuffer_FillInfo(view, self, bl->value, bl->size, 0, flags);
        }

        string Message::Blob::decode(string encoding)
        {
            if (encoding == "") {
                string _mime_type = _bl->mime_type ? _bl->mime_type : "";
                encoding = "ascii";

                if (_mime_type == "application/pEp.sync")
                    encoding = "pep.sync";

                if (_mime_type == "application/pEp.keyreset")
                    encoding = "pep.distribution";

            }
            object codecs = import("codecs");
            object _decode = codecs.attr("decode");
            return call< string >(_decode.ptr(), this, encoding);
        }

        PyBufferProcs Message::Blob::bp = { getbuffer, NULL };

        Message::Message(int dir, Identity *from)
            : _msg(new_message((PEP_msg_direction) dir), &free_message)
        {
            if (!_msg)
                throw bad_alloc();

            if (from) {
                _msg->from = ::identity_dup(*from);
                if (!_msg->from)
                    throw bad_alloc();
                _msg->dir = (PEP_msg_direction) dir;
            }
        }

        Message::Message(string mimetext)
            : _msg(NULL, &free_message)
        {
            message *_cpy;
            PEP_STATUS status = mime_decode_message(mimetext.c_str(),
                    mimetext.size(), &_cpy, NULL);
            switch (status) {
                case PEP_STATUS_OK:
                    if (_cpy)
                        _cpy->dir = PEP_dir_outgoing;
                    else
                        _cpy = new_message(PEP_dir_outgoing);

                    if (!_cpy)
                        throw bad_alloc();

                    _msg = shared_ptr< message >(_cpy);
                    break;

                case PEP_BUFFER_TOO_SMALL:
                    throw runtime_error("mime_decode_message: buffer too small");

                case PEP_CANNOT_CREATE_TEMP_FILE:
                    throw runtime_error("mime_decode_message: cannot create temp file");

                case PEP_OUT_OF_MEMORY:
                    throw bad_alloc();

                default:
                    stringstream build;
                    build << "mime_decode_message: unknown error (" << (int) status << ")";
                    throw runtime_error(build.str());
            }
        }

        Message::Message(const Message& second)
            : _msg(second._msg)
        {
            if (!_msg.get())
                throw bad_alloc();
        }

        Message::Message(message *msg)
            : _msg(::message_dup(msg), &free_message)
        {

        }

        Message::~Message()
        {

        }

        Message::operator message *()
        {
            return _msg.get();
        }

        Message::operator const message *() const
        {
            return _msg.get();
        }

        string Message::_str()
        {
            if (!(_msg->from && _msg->from->address && _msg->from->address[0]))
                throw out_of_range(".from_.address missing");

            char *mimetext;
            string result;

            PEP_STATUS status = mime_encode_message(*this, false, &mimetext, false);
            switch (status) {
                case PEP_STATUS_OK:
                    result = mimetext;
                    free(mimetext);
                    break;

                case PEP_BUFFER_TOO_SMALL:
                    throw runtime_error("mime_encode_message: buffer too small");

                case PEP_CANNOT_CREATE_TEMP_FILE:
                    throw runtime_error("mime_encode_message: cannot create temp file");

                case PEP_OUT_OF_MEMORY:
                    throw bad_alloc();

                default:
                    stringstream build;
                    build << "mime_encode_message: unknown error (" << (int) status << ")";
                    throw runtime_error(build.str());
            }

            return result;
        }

        string Message::_repr()
        {
            stringstream build;
            build << "Message(" << repr(_str()) << ")";
            return build.str();
        }

        boost::python::tuple Message::attachments()
        {
            boost::python::list l;

            for (bloblist_t *bl = _msg->attachments; bl && bl->value; bl =
                    bl->next) {
                l.append(Blob(bl, true));
            }

            return boost::python::tuple(l);
        }

        void Message::attachments(boost::python::list value)
        {
            bloblist_t *bl = new_bloblist(NULL, 0, NULL, NULL);
            if (!bl)
                throw bad_alloc();

            bloblist_t *_l = bl;
            for (int i=0; i<len(value); i++) {
                Message::Blob& blob = extract< Message::Blob& >(value[i]);
                _l = bloblist_add(_l, blob._bl->value, blob._bl->size,
                        blob._bl->mime_type, blob._bl->filename);
                if (!_l) {
                    for (_l = bl; _l && _l->value; ) {
                        free(_l->mime_type);
                        free(_l->filename);
                        bloblist_t *_ll = _l;
                        _l = _l->next;
                        free(_ll);
                    }
                    throw bad_alloc();
                }
            }

            for (int i=0; i<len(value); i++) {
                Message::Blob& blob = extract< Message::Blob& >(value[i]);
                blob._bl->value = NULL;
                blob._bl->size = 0;
                free(blob._bl->mime_type);
                blob._bl->mime_type = NULL;
                free(blob._bl->filename);
                blob._bl->filename = NULL;
            }

            free_bloblist(_msg->attachments);
            _msg->attachments = bl;
        }

        Message Message::encrypt()
        {
            boost::python::list extra;
            return encrypt_message(*this, extra, PEP_enc_PGP_MIME, 0);
        }

        Message Message::_encrypt(boost::python::list extra, int enc_format, int flags)
        {
            if (!enc_format)
                enc_format = PEP_enc_PGP_MIME;
            return encrypt_message(*this, extra, enc_format, flags);
        }

        boost::python::tuple Message::decrypt(int flags) {
            return pEp::PythonAdapter::decrypt_message(*this, flags);
        }

        PEP_rating Message::outgoing_rating()
        {
            if (_msg->dir != PEP_dir_outgoing)
                throw invalid_argument("Message.dir must be outgoing");

            if (from().address() == "")
                throw invalid_argument("from.address needed");
            if (from().username() == "")
                throw invalid_argument("from.username needed");

            if (len(to()) + len(cc()) == 0)
                throw invalid_argument("either to or cc needed");

            PEP_STATUS status = myself(adapter.session(), _msg->from);
            _throw_status(status);

            PEP_rating rating = PEP_rating_undefined;
            status = outgoing_message_rating(adapter.session(), *this, &rating);
            _throw_status(status);

            return rating;
        }

        PEP_color Message::outgoing_color()
        {
            return _color(outgoing_rating());
        }

        Message Message::copy()
        {
            message *dup = message_dup(*this);
            if (!dup)
                throw bad_alloc();
            return Message(dup);
        }

        Message Message::deepcopy(dict&)
        {
            return copy();
        }

        Message outgoing_message(Identity me)
        {
            if (me.address().empty() || me.user_id().empty())
                throw runtime_error("at least address and user_id of own user needed");

            ::myself(adapter.session(), me);
            auto m = Message(PEP_dir_outgoing, &me);
            return m;
        }

        static object update(Identity ident)
        {
            if (ident.address().empty())
                throw runtime_error("at least address needed");
            update_identity(adapter.session(), ident);
            return object(ident);
        }

        static boost::python::list update(boost::python::list il)
        {
            for (int i=0; i<len(il); i++) {
                update(extract< Identity >(il[i]));
            }

            return il;
        }

        Message incoming_message(string mime_text)
        {
            auto m = Message(mime_text);
            m.dir(PEP_dir_incoming);

            try {
                m.from(update(m.from()));
            }
            catch (out_of_range&) { }

            try {
                m.recv_by(update(m.recv_by()));
            }
            catch (out_of_range&) { }

            m.to(update(m.to()));
            m.cc(update(m.cc()));
            m.reply_to(update(m.reply_to()));

            return m;
        }
    }
}
