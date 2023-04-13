// This file is under GNU Affero General Public License 3.0
// see LICENSE.txt

// System
#include <iostream> /////////////////////////////////////////////////
#include <cstdlib>
#include <cstring>
#include <stdexcept>
#include <sstream>
#include <vector>
#include <Python.h>

// Engine
#include <pEp/mime.h>
#include <pEp/keymanagement.h>
#include <pEp/message_api.h>
#include <pEp/mixnet.h>

// local
#include "message.hh"
#include "message_api.hh"

namespace pEp {
    namespace PythonAdapter {
        using namespace boost::python;

        Message::Blob::Blob(bloblist_t *bl, bool chained) : _bl(bl), part_of_chain(chained)
        {
            if (!_bl) {
                throw std::bad_alloc();
            }
            std::cerr << "Built a blob at " << this << " from a C bloblist (chained? " << chained << ")\n";
            std::cerr << "  its _bl is at " << _bl << "\n";
        }

        Message::Blob::Blob(object data, string mime_type, string filename) :
            _bl(new_bloblist(NULL, 0, NULL, NULL)),
            part_of_chain(false)
        {
            if (!_bl) {
                throw std::bad_alloc();
            }

            Py_buffer src;
            int result = PyObject_GetBuffer(data.ptr(), &src, PyBUF_CONTIG_RO);
            if (result) {
                throw invalid_argument("need a contiguous buffer to read");
            }

            char *mem = (char *)malloc(src.len);
            if (!mem) {
                PyBuffer_Release(&src);
                throw std::bad_alloc();
            }

            memcpy(mem, src.buf, src.len);
            std::cerr << "  copied old cd " << src.buf << " ...\n";
            std::cerr << "  ... to        " << mem << " ...\n";
            free(_bl->value);
            std::cerr << "  keeping _bl   " << _bl << "\n";
            std::cerr << "  freed value   " << (void*) _bl->value << "\n";
            _bl->size = src.len;
            _bl->value = mem;
            std::cerr << "  replaced with " << (void*) _bl->value << "\n";

            PyBuffer_Release(&src);

            this->mime_type(mime_type);
            this->filename(filename);
            std::cerr << "Built a blob at " << this << " from a C++ data object\n";
            std::cerr << "  its _bl is at " << _bl << "\n";
        }

        Message::Blob::Blob(const Message::Blob &second) : _bl(second._bl), part_of_chain(second.part_of_chain) {
            std::cerr << "Built a blob at " << this << " as a copy of " << & second << " which " << (second.part_of_chain ? "WAS" : "was NOT") << " part of a chain\n";
            if (! part_of_chain) {
                // Replace _bc with a copy.
                char *data_c = NULL;
                data_c = (char*) malloc(_bl->size);
                if (data_c == NULL)
                    throw std::bad_alloc();
                memcpy(data_c, _bl->value, _bl->size);
                bloblist_t *_new_bl = new_bloblist(data_c, _bl->size, _bl->mime_type, NULL);
                if (_new_bl == NULL) {
                    free(data_c);
                    throw std::bad_alloc();
                }
                _bl = _new_bl;
            }
            std::cerr << "  its _bl is at " << _bl << "\n";
        }

        Message::Blob::~Blob()
        {
            std::cerr << "Destroy blob at " << this << "\n";
            std::cerr << "  its _bl was at" << _bl << (part_of_chain ? " (NOT destroying it)" : "(DESTROYING it)") << "\n";
            if (!part_of_chain) {
                free(_bl->value);
                std::cerr << "  freed c_data  " << (void*) _bl->value << "\n";
                free(_bl);
                std::cerr << "  freed _bl     " << (void*) _bl << "\n";
            }
        }

        string Message::Blob::_repr()
        {
            std::stringstream build;
            build << "Blob(";
            if (!_bl) {
                build << "b'', '', ''";
            } else {
build << "@ " << this << " _bl " << (void*) _bl << "  c_data " << (void*) _bl->value << " " ;
//build << "\"" << (char *)_bl->value << "\""; // only for debugging, of course: dangerous unless '\0'-terminated
build << " ";
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

        int Message::Blob::getbuffer(PyObject *self, Py_buffer *view, int flags)
        {
            bloblist_t *bl = NULL;

            try {
                Message::Blob &blob = extract<Message::Blob &>(self);
                bl = blob._bl;
            } catch (std::exception &e) {
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

                if (_mime_type == "application/pEp.sync") {
                    encoding = "pep.sync";
                }

                if (_mime_type == "application/pEp.keyreset") {
                    encoding = "pep.distribution";
                }
            }
            object codecs = import("codecs");
            object _decode = codecs.attr("decode");
            return call<string>(_decode.ptr(), this, encoding);
        }

        PyBufferProcs Message::Blob::bp = { getbuffer, NULL };

        Message::Message(int dir, Identity *from) :
            _msg(new_message((PEP_msg_direction)dir), &free_message)
        {
            if (!_msg) {
                throw std::bad_alloc();
            }

            if (from) {
                _msg->from = ::identity_dup(*from);
                if (!_msg->from) {
                    throw std::bad_alloc();
                }
                _msg->dir = (PEP_msg_direction)dir;
            }
        }

        Message::Message(string mimetext) : _msg(NULL, &free_message)
        {
            message *_cpy;
            PEP_STATUS status = mime_decode_message(mimetext.c_str(), mimetext.size(), &_cpy, NULL);
            switch (status) {
                case PEP_STATUS_OK:
                    if (_cpy) {
                        _cpy->dir = PEP_dir_outgoing;
                    } else {
                        _cpy = new_message(PEP_dir_outgoing);
                    }

                    if (!_cpy) {
                        throw std::bad_alloc();
                    }

                    _msg = shared_ptr<message>(_cpy);
                    break;

                case PEP_BUFFER_TOO_SMALL:
                    throw runtime_error("mime_decode_message: buffer too small");

                case PEP_CANNOT_CREATE_TEMP_FILE:
                    throw runtime_error("mime_decode_message: cannot create temp file");

                case PEP_OUT_OF_MEMORY:
                    throw std::bad_alloc();

                default:
                    std::stringstream build;
                    build << "mime_decode_message: unknown error (" << (int)status << ")";
                    throw runtime_error(build.str());
            }
        }

        Message::Message(const Message &second) : _msg(second._msg)
        {
            if (!_msg.get()) {
                throw std::bad_alloc();
            }
        }

        Message::Message(message *msg) : _msg(::message_dup(msg), &free_message) {}

        Message::~Message() {}

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
            if (!(_msg->from && _msg->from->address && _msg->from->address[0])) {
                throw std::out_of_range(".from_.address missing");
            }

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
                    throw std::bad_alloc();

                default:
                    std::stringstream build;
                    build << "mime_encode_message: unknown error (" << (int)status << ")";
                    throw runtime_error(build.str());
            }

            return result;
        }

        string Message::_repr()
        {
            std::stringstream build;
            build << "Message(" << repr(_str()) << ")";
            return build.str();
        }

        boost::python::tuple Message::attachments()
        {
            boost::python::list l;

            for (bloblist_t *bl = _msg->attachments; bl && bl->value; bl = bl->next) {
                l.append(Blob(bl, true));
            }

            return boost::python::tuple(l);
        }

        void Message::attachments(boost::python::list value)
        {
            bloblist_t *bl = new_bloblist(NULL, 0, NULL, NULL);
            if (!bl) {
                throw std::bad_alloc();
            }

            bloblist_t *_l = bl;
            for (int i = 0; i < len(value); i++) {
                Message::Blob &blob = extract<Message::Blob &>(value[i]);
                _l = bloblist_add(
                    _l,
                    blob._bl->value,
                    blob._bl->size,
                    blob._bl->mime_type,
                    blob._bl->filename);
                if (!_l) {
                    for (_l = bl; _l && _l->value;) {
                        free(_l->mime_type);
                        free(_l->filename);
                        bloblist_t *_ll = _l;
                        _l = _l->next;
                        free(_ll);
                    }
                    throw std::bad_alloc();
                }
            }

            for (int i = 0; i < len(value); i++) {
                Message::Blob &blob = extract<Message::Blob &>(value[i]);
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
            if (!enc_format) {
                enc_format = PEP_enc_PGP_MIME;
            }
            return encrypt_message(*this, extra, enc_format, flags);
        }

        boost::python::tuple Message::decrypt(int flags)
        {
            return pEp::PythonAdapter::decrypt_message(*this, flags);
        }

        PEP_rating Message::outgoing_rating()
        {
            if (_msg->dir != PEP_dir_outgoing) {
                throw invalid_argument("Message.dir must be outgoing");
            }

            if (from().address() == "") {
                throw invalid_argument("from.address needed");
            }
            if (from().username() == "") {
                throw invalid_argument("from.username needed");
            }

            if (len(to()) + len(cc()) == 0) {
                throw invalid_argument("either to or cc needed");
            }

            PEP_STATUS status = myself(Adapter::session(), _msg->from);
            _throw_status(status);

            PEP_rating rating = PEP_rating_undefined;
            status = outgoing_message_rating(Adapter::session(), *this, &rating);
            _throw_status(status);

            return rating;
        }

        PEP_color Message::outgoing_color()
        {
            return _color(outgoing_rating());
        }

        Message Message::onionize(boost::python::list relays)
        {
            return onionize(relays, boost::python::list(), (int) PEP_enc_PEP_message_v2, (int) PEP_encrypt_flag_default);
        }
        Message Message::onionize(boost::python::list relays, boost::python::list extra)
        {
            return onionize(relays, extra, (int) PEP_enc_PEP_message_v2, (int) PEP_encrypt_flag_default);
        }
        Message Message::onionize(boost::python::list relays, boost::python::list extra, int enc_format)
        {
            return onionize(relays, extra, enc_format, (int) PEP_encrypt_flag_default);
        }
        Message Message::onionize(boost::python::list relays, boost::python::list extra, int enc_format, int flags)
        {
            ::identity_list *identities_c = NULL;
            PEP_STATUS status = PEP_STATUS_OK;

            // In case of any error, be it memory allocation or type conversion,
            // free our temporary data before re-throwing to the caller.
            ::pEp_identity *identity_c = NULL;
            stringlist_t *extra_c = NULL;
            try {
                // Turn Python lists into C lists.
                extra_c = to_stringlist(extra);
                for (int i = len(relays) - 1; i >= 0; i--) {
                    Identity &identity = boost::python::extract<Identity &>(relays [i]);
                    ::identity_list *new_identities_c = identity_list_cons_copy(identity, identities_c);
                    if (new_identities_c == NULL)
                        throw std::bad_alloc();
                    identities_c = new_identities_c;
                }

                // Call the C function to do the actual work.
                ::message *in_message_c = * this;
                ::message *out_message_c = NULL;
                status = ::onionize(Adapter::session(), in_message_c, extra_c, &out_message_c, (::PEP_enc_format) enc_format, (::PEP_encrypt_flags_t) flags, identities_c);
                _throw_status(status);

                // Success.
                free_stringlist(extra_c);
                free_identity_list(identities_c);
                return out_message_c;
            } catch (const std::exception &e) {
                free_identity(identity_c);
                free_stringlist(extra_c);
                free_identity_list(identities_c);
                throw e;
            }
        }

        Message Message::copy()
        {
            message *dup = message_dup(*this);
            if (!dup) {
                throw std::bad_alloc();
            }
            return Message(dup);
        }

        Message Message::deepcopy(dict &)
        {
            return copy();
        }

        Message::Blob Message::serialize()
        {
            std::cerr << "Message::serialize this is   " << this << "\n";
            size_t length_in_bytes_c;
            char *data_c = NULL;
            ::bloblist_t *blob_c;

            /* Serialise the message into a memory buffer. */
            PEP_STATUS status = onion_serialize_message(Adapter::session(), *this, &data_c, &length_in_bytes_c);
            _throw_status(status);

            /* Turn the memory buffer into a blob. */
            blob_c = new_bloblist(data_c, length_in_bytes_c, PEP_ONION_MESSAGE_MIME_TYPE, NULL);
            if (blob_c == NULL) {
                ::free(data_c);
                throw std::bad_alloc();
            }
            return Message::Blob(blob_c, false);
            /*
            char *data_c = strdup("foo!");
            size_t length_in_bytes_c = strlen(data_c);
            ::bloblist_t *blob_c = NULL;
            blob_c = ::new_bloblist(data_c, length_in_bytes_c, PEP_ONION_MESSAGE_MIME_TYPE, NULL);
            if (blob_c == NULL) {
                ::free(data_c);
                throw std::bad_alloc();
            }
            std::cerr << "Message::serialize data_c is " << (void*) data_c << "\n";
            std::cerr << "Message::serialize blob_c is " << blob_c << "\n";
            return Message::Blob(blob_c, false);
            */
        }

        Message deserialize(const Message::Blob &blob)
        {
            const char *data_c = blob.c_data();
            size_t length_in_bytes_c = blob.size();
            message *msg = NULL;
            PEP_STATUS status = onion_deserialize_message(Adapter::session(), data_c, length_in_bytes_c, &msg);
            _throw_status(status);

            return Message(msg);
        }

        Message outgoing_message(Identity me)
        {
            if (me.address().empty() || me.user_id().empty()) {
                throw runtime_error("at least address and user_id of own user needed");
            }

            ::myself(Adapter::session(), me);
            auto m = Message(PEP_dir_outgoing, &me);
            return m;
        }

        static object update(Identity ident)
        {
            if (ident.address().empty()) {
                throw runtime_error("at least address needed");
            }
            update_identity(Adapter::session(), ident);
            return object(ident);
        }

        static boost::python::list update(boost::python::list il)
        {
            for (int i = 0; i < len(il); i++) {
                update(extract<Identity>(il[i]));
            }

            return il;
        }

        Message incoming_message(string mime_text)
        {
            auto m = Message(mime_text);
            m.dir(PEP_dir_incoming);

            try {
                m.from(update(m.from()));
            } catch (std::out_of_range &) {
            }

            try {
                m.recv_by(update(m.recv_by()));
            } catch (std::out_of_range &) {
            }

            m.to(update(m.to()));
            m.cc(update(m.cc()));
            m.reply_to(update(m.reply_to()));

            return m;
        }

    } // namespace PythonAdapter
} // namespace pEp
