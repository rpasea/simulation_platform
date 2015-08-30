#!/usr/bin/python

from simulation_platform.networking.communicator import communicator
from simulation_platform.message import message
from simulation_platform.message import buffer
import time


class mock_listener:
    def __init__(self):
        self.buffer = buffer.MessageBuffer()
    def received_data(self, address, data):
        self.buffer.add_data(data)
        while self.buffer.has_messages():
            msg = self.buffer.get_message()
            if message.types[msg.type] == 'NetworkQueryMessage':
                print msg.address, msg.netmask 

if __name__ == "__main__":
    comm1 = communicator(mock_listener(), 7600)
    comm2 = communicator(mock_listener(), 7601)
    
    comm1.start()
    comm2.start()
    
    time.sleep(1)

    comm1.connect('localhost' , 7601)

    time.sleep(1)
    msg = message.NetworkQueryMessage('1234', '5678')
    data = str(message.SerializedMessage(msg))
    #print 'Sending ', data
    
    comm2.send('127.0.0.1', data)
    
    time.sleep(3)
    comm2.send('127.0.0.1', data)
    time.sleep(3)
    comm1.stop()
    comm2.stop()
    
