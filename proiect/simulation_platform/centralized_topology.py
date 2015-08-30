'''
Created on May 1, 2015

@author: radu
'''
from networking import communicator
import threading

from message import message
from message.message import SerializedMessage
from message.message import RoutingMessage
from message import buffer

class CentralizedTopology(object):
    '''
    classdocs
    '''


    def __init__(self, start_port = communicator.PORT, simulation = None):
        '''
        Constructor
        '''
        self.root = False
        self.communicator = communicator.communicator(self, start_port)
        self.root_addr = None
        self.buffers = {}
        self.routing_table = {}
        self.node = None
        self.local_id = None
        self.id_counter = 1
        self.lock = threading.Lock()
        self.id_sem = threading.Semaphore(0)
        self.identify_sem = threading.Semaphore(0)
        self.simulation = simulation
    
    def start(self, node, root_addr_tuple = None):
        self.node = node
        self.communicator.start()
        if root_addr_tuple is None:
            self.local_id = 0
            self.root = True
        else:
            self.root_addr = root_addr_tuple
            self.buffers[self.root_addr[0]] = buffer.MessageBuffer()
            self.routing_table[0] = self.root_addr[0]
            self.routing_table[self.root_addr[0]] = 0
            self.communicator.connect(root_addr_tuple[0], root_addr_tuple[1])
            self.get_local_id()
    def stop(self):
        self.communicator.stop()
        self.node.stop()
        
    def received_data(self, address, data):
        if address not in self.buffers:
            self.buffers[address] = buffer.MessageBuffer()
        b = self.buffers[address]
        b.add_data(data)
        while b.has_messages():
            self.treat_msg(b.get_message(), address)
            
    def get_local_id(self):
        if self.local_id is not None:
            return self.local_id
        data = str(message.SerializedMessage(message.IdRequest()))
        self.communicator.send(self.root_addr[0], data)
        self.id_sem.acquire()
        return self.local_id
        
    def route_msg(self, routing_message, address):
        if routing_message.dest_id == self.local_id or \
           routing_message.dest_id == -1:
            self.treat_msg(routing_message.message, address)
            return
        if self.root:
            if routing_message.dest_id == -1:
                data = str(routing_message)
                for addr in self.buffers:
                    if addr != self.routing_table[routing_message.dest_id]:
                        self.communicator.send(addr, data)
            elif routing_message.dest_id in self.routing_table:
                data = str(routing_message)
                addr = self.routing_table[routing_message.dest_id]
                self.communicator.send(addr, data)
    
    def id_request(self, msg, address):
        with self.lock:
            id = self.id_counter
            self.id_counter += 1
        
        self.routing_table[id] = address
        self.routing_table[address] = id
        data = str(message.SerializedMessage(message.IdReply(id)))
        self.communicator.send(address, data)
        
    def address_of_id(self, id):
        if id in self.routing_table:
            return self.routing_table[id]
        if self.root:
            return None
        data = str(message.SerializedMessage(message.IdentifyRequest(id)))
        self.communicator.send(self.root_addr[0], data)
        self.identify_sem.acquire()
        if id in self.routing_table:
            return self.routing_table[id]
        else:
            return None
        
    def id_reply(self, msg, address):
        self.local_id = msg.id
        self.id_sem.release()
    
    def local_message(self, message, address):
        if address in self.routing_table:
            self.node.received_message(message, self.routing_table[address])
            
    def send_message(self, message, dest_id):
        msg = SerializedMessage(RoutingMessage(self.local_id, dest_id, message))
        if self.root:
            addr = self.routing_table[dest_id]
            if addr is None:
                return False
        else:
            addr = self.routing_table[0]
            if addr is None:
                return False
        self.communicator.send(addr, str(msg))
        return True
    
    def broadcast(self, message):
        msg = SerializedMessage(RoutingMessage(self.local_id, -1, message))
        data = str(msg)
        if self.root:
            for addr in self.buffers:
                self.communicator.send(addr, data)
        else:
            addr = self.routing_table[0]
            if addr is not None:
                self.communicator.send(addr, data)
    
    def identify_request(self, msg, address):
        if msg.id in self.routing_table:
            addr = self.routing_table[msg.id]
        else:
            addr = None
        data = str(message.SerializedMessage(message.IdentifyReply(msg.id, addr)))
        self.communicator.send(address, data)
    
    def identify_reply(self, msg, address):
        if msg.address is not None:
            self.routing_table[msg.address] = msg.id
            self.routing_table[msg.id] = msg.address
        self.identify_sem.release()
        
    def simulation_message(self, msg, address):
        if self.simulation is not None:
            self.simulation.received_message(msg.msg, address)
    
    def treat_msg(self, msg, address):
        type = message.types[msg.type]
        if type == 'IdRequest':
            self.id_request(msg, address)
        elif type == 'IdReply':
            self.id_reply(msg, address)
        elif type == 'RoutingMessage':
            self.route_msg(msg, address)
        elif type == 'IdentifyRequest':
            self.identify_request(msg, address)
        elif type == 'IdentifyReply':
            self.identify_reply(msg, address)
        elif type == 'SimulationMessage':
            self.simulation_message(msg, address)
        else:
            self.local_message(msg, address)
