import threading

from network import network
from message import message
from simulation_platform.virtualbox_controller import vbox_controller

class InvalidOperation(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class simulator_node:
    def __init__(self, topology):
        self.containers = {}
        self.networks = {}
        self.lock = threading.Lock()
        self.topology = topology
        
    def stop(self):
        for net in self.networks:
            self.networks[net].stop()
        for container in self.containers:
            self.containers[container].stop()
            
    def start_container(self, name):
        with self.lock:
            container = vbox_controller(name)
            container.lock_session()
            container.connect_adb()
            self.containers[name] = container

    def create_network(self, address, netmask, name_suffix = ''):
        print 'Creating network ' , address, ':', netmask
        net = network(address, netmask, name_suffix, self)
        if net.key() not in self.networks:
            net.start()
            net.root = True
            self.networks[net.key()] = net
            msg = message.NetworkQueryMessage(address, netmask)
            self.topology.broadcast(msg)

    def move_container_to_network(self, container, address, netmask, network_name_suffix = ''):
        print 'Moving container ', container, ' to network: ', address, ':', netmask
        if container not in self.containers:
            raise InvalidOperation("Don't have container + " + container + ".")
 
        with self.lock:
            net = network(address, netmask)
            if net.key() not in self.networks:
                self.create_network(address, netmask, network_name_suffix)
            net = self.networks[net.key()]
                
            if self.containers[container].network_key in self.networks:
                self.networks[container.network_key].detach_container(container)
                if not self.networks[container.network_key].used:
                    self.networks[container.network_key].stop()
                    del self.networks[container.network_key]
            net.attach_container(self.containers[container])

    def add_container(self, container):
        with self.lock:
            name = container.name
            if name not in self.containers:
                self.containers[name] = container
        
    def remove_container(self, container):
        with self.lock:
            if container.name in self.containers:
                del self.containers[container.name]
    
    def unknown_message(self, msg, source):
        pass
    
    def network_query(self, query_msg, source):
        with self.lock:
            net = network(query_msg.address, query_msg.netmask)
            if net.key() in self.networks:
                net = self.networks[net.key()]
                if net.root:
                    switch = net.switch_name()
                    msg = message.NetworkReplyMessage(query_msg.address, query_msg.netmask, switch)
                    self.topology.send_message(msg, source)
    
    def network_reply(self, reply_msg, source):
        addr = self.topology.address_of_id(source)
        if addr is not None:
            with self.lock:
                net = network(reply_msg.address, reply_msg.netmask)
                if net.key() in self.networks:
                    net = self.networks[net.key()]
                    net.root = False
                    net.root_id = source
                    net.reattach_containers()
                    net.wire(addr, reply_msg.switch)
                

    def received_message(self, msg, source):
        type = message.types[msg.type]
        if type == 'NetworkQueryMessage':
            self.network_query(msg, source)
        elif type == 'NetworkReplyMessage':
            self.network_reply(msg, source)
        elif type == 'ChangeNetworkMessage':
            self.move_container_to_network(msg.vm, msg.address, msg.netmask)
        elif type == 'NetworkMessage':
            if msg.key in self.networks:
                net = self.networks[msg.key]
                net.received_message(msg.msg, source)    
        else:
            self.unknown_message(msg, source)
            
    def send_network_message(self, msg, dest, network):
        net_msg = message.NetworkMessage(network.key(), msg)
        self.topology.send_message(net_msg, dest)

                            