#include <Python.h>
#include "message.hh"
#include <stdlib.h>
#include <string.h>
#include <stdexcept>

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
            _bl(bloblist_dup(second._bl)), part_of_chain(false)
        {
            if (!_bl)
                throw bad_alloc();
        }

        Message::Blob::~Blob()
        {
            if (!part_of_chain) {
                free(_bl->value);
                free(_bl);
            }
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

        PyBufferProcs Message::Blob::bp = { getbuffer, NULL };

        Message::Message(PEP_msg_direction dir)
            : _msg(new_message(dir))
        {
            if (!_msg)
                throw bad_alloc();
        }

        Message::Message(const Message& second)
            : _msg(message_dup(second._msg))
        {
            if (!_msg)
                throw bad_alloc();
        }

        Message::Message(message *msg)
            : _msg(msg)
        {

        }

        Message::~Message()
        {
            free_message(_msg);
        }

        void Message::attach(message *msg)
        {
            free_message(_msg);
            _msg = msg;
        }

        message *Message::detach()
        {
            message *new_one = new_message(_msg->dir);
            if (!new_one)
                throw bad_alloc();

            message *msg = _msg;
            _msg = new_one;

            return msg;
        }

        Message::operator message *()
        {
            if (!_msg)
                throw bad_cast();
            return _msg;
        }

        tuple Message::attachments()
        {
            list l;

            for (bloblist_t *bl = _msg->attachments; bl && bl->value; bl =
                    bl->next) {
                l.append(Blob(bl, true));
            }

            return tuple(l);
        }

        void Message::attachments(list value)
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
    }
}
