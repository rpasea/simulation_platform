import ipaddress
import threading
import subprocess
from message import message


class network:
    def __init__(self, address, netmask, name_suffix = '', simulation_node = None):
        self.network = ipaddress.IPv4Network(address + '/' + netmask)
        self.used_ips = []
        self.containers = {}
        self.name = 'sw_' + address + '_' + netmask + name_suffix
        self.used = False
        self.lock = threading.Lock()
        self.root = False
        self.root_id = None
        self.pipe_proc = None
        self.node = simulation_node
        self.address_queue = []
        self.address_lock = threading.Lock()
        self.address_callbacks = []

    def start(self):
        subprocess.call('vde_switch -d -s /tmp/' + self.name + ' -M /tmp/' + self.name + '_mgmt', shell = True)

    def stop(self):
        containers = []
        for container in self.containers:
            containers.append(container)
        for container in containers:
            self.detach_container(container)
        if self.pipe_proc is not None:
            self.pipe_proc.terminate()
        subprocess.call('pkill -f "vde_switch -d -s /tmp/' + self.name + 'name_suffix"', shell = True)

    def reserve_address(self, callback = None):
        if self.root:
            for addr in self.network.hosts():
                if addr not in self.used_ips:
                    self.used_ips.append(addr)
                    return addr
        else:
            if self.address_queue:
                with self.address_lock:
                    if self.address_queue: # we have one
                        return self.address_queue.pop()
            # we don't have ips, make a request
            if callback is not None:
                with self.address_lock:
                    self.address_callbacks.append(callback)
            msg = message.IpRequest()
            print 'Sending ip request'
            self.node.send_network_message(msg, self.root_id, self)
        return None
    
    def release_address(self, address):
        if self.root:
            self.used_ips.remove(address)
        else:
            msg = message.IpRelease(address)
            self.node.send_network_message(msg, self.root_id, self)
    
    def switch_name(self):
        return '/tmp/' + self.name

    def attach_container(self, container):
        with self.lock:
            container_addr = self.reserve_address((self.attach_container, [container]))
            if container_addr is not None:
                self.containers[container] = container_addr
                net_tuple = self.network.with_netmask.partition('/')
                container.attach_to_switch(self.name)
                container.move_to_lan(str(container_addr), net_tuple[2], self.key())
                self.used = True

    def detach_container(self, container):
        with self.lock:
            if container in self.containers:
                container.attach_to_switch(None)
                if self.root:
                    self.used_ips.remove(self.containers[container])
                del self.containers[container]
                if not self.containers: # check if containers is empty
                        self.used = False
    def reattach_containers(self):
        containers = []
        for container in self.containers:
            containers.append(container)
        for container in containers:
            self.detach_container(container)
            self.attach_container(container)

    def wire(self, host, switch_name = None):
        if switch_name is None:
            switch_name = self.switch_name()
        with self.lock:
            if self.pipe_proc is not None:
                self.pipe_proc.terminate()
            cmd = 'dpipe vde_plug ' + self.switch_name() + ' = ssh ' + host + ' vde_plug ' + switch_name
            self.pipe_proc = subprocess.Popen(cmd, shell = True)
        
    def key(self):
        return self.network.with_netmask

    def is_used(self):
        return self.used or self.root
    
    def received_message(self, msg, source):
        type = message.types[msg.type]
        if type == 'IpRequest':
            if self.root:
                with self.lock:
                    ip = self.reserve_address()
                print 'Sending ip ' , ip
                self.node.send_network_message(message.IpResponse(ip), source, self)
        elif type == 'IpRelease':
            if self.root:
                with self.lock:
                    self.used_ips.remove(ip)
        elif type == 'IpResponse':
            callback = None
            with self.address_lock:
                self.address_queue.append(msg.ip)
                callback = self.address_callbacks.pop()
            if callback is not None:
                callback[0](*callback[1])
        else:
            pass