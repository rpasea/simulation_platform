import message
import struct

class MessageBuffer:
    def __init__(self):
        self.size_buffer = ''
        self.expected_size = None
        self.buffer = ''
        self.messages = []

    def has_messages(self):
        return len(self.messages) > 0

    def get_message(self):
        if self.has_messages():
            return self.messages.pop(0)

    def add_data(self, data):
        while len(data) > 0:
            if self.expected_size is None:
                to_read = min(message.int_size - len(self.size_buffer),
                              len(data))
                self.size_buffer += data[ : to_read]
                data = data[to_read : ]
                if len(self.size_buffer) == message.int_size:
                    self.expected_size = struct.unpack('>I', self.size_buffer)[0]
                    self.size_buffer = ''
            if len(data) > 0:
                to_read = min(self.expected_size - len(self.buffer),
                              len(data))
                self.buffer += data[ : to_read]
                data = data[to_read : ]
                if self.expected_size == len(self.buffer):
                    self.messages.append(message.
                                         SerializedMessage(self.buffer, False).
                                         get_message())
                    self.buffer = ''
                    self.expected_size = None
                                        
