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

        Message::Blob::Blob(const Blob& second)
        {
            _size = second._size;
            _value = (char *) malloc(_size);
            if (!_value)
                throw bad_alloc();
            memcpy(_value, second._value, _size);
            _mime_type = second._mime_type;
            _filename = second._filename;
        }

        Message::Blob::~Blob()
        {
            free(_value);
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

