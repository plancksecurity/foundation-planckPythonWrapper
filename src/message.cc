#include "message.hh"

namespace pEp {
    namespace PythonAdapter {
        using namespace std;

        Message::Message()
            : _msg(new_message(NULL, NULL, NULL, NULL))
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
            message *new_one = new_message(NULL, NULL, NULL, NULL);
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

