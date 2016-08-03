#include "message.hh"
#include <stdlib.h>

namespace pEp {
    namespace PythonAdapter {
        using namespace std;

        Message::Blob::Blob(char *value, size_t size, string mime_type,
                string filename) : _value(value), _size(size),
                _mime_type(mime_type), _filename(filename)
        {

        }

        Message::Blob::Blob(const Blob& second, bool copy)
        {
            _size = second._size;
            if (copy) {
                _value = (char *) malloc(_size);
                if (!_value)
                    throw bad_alloc();
                memcpy(_value, second._value, _size);
            }
            else {
                _value = second._value;
            }
            _mime_type = second._mime_type;
            _filename = second._filename;
        }

        Message::Blob::~Blob()
        {
            free(_value);
        }

        void Message::Blob::attach(bloblist_t *blob)
        {
            free(_value);
            _size = blob->size;
            _value = blob->value;
            blob->size = 0;
            blob->value = NULL;
            if (blob->mime_type) {
                _mime_type = blob->mime_type;
                free(blob->mime_type);
                blob->mime_type = NULL;
            }
            if (blob->filename) {
                _filename = blob->filename;
                free(blob->filename);
                blob->filename = NULL;
            }
        }

        bloblist_t * Message::Blob::detach()
        {
            bloblist_t *bl = new_bloblist(_value, _size, _mime_type.c_str(),
                    _filename.c_str());
            if (!bl)
                throw bad_alloc();
            _size = 0;
            _value = NULL;
            _mime_type = "";
            _filename = "";
            return bl;
        }

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
    }
}

