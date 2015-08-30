'''
Created on May 16, 2015

@author: radu
'''
import threading
import sys
import time

from centralized_topology import CentralizedTopology
from simulator_node import simulator_node
from virtualbox_controller import clone_vm
from virtualbox_controller import vbox_controller
from event_queue import simulation_event_queue

from message import message

def start_topology(port, root_addr, root_port, simulation):
    top = CentralizedTopology(port, simulation)
    node = simulator_node(top)
    if root_addr is None:
        top.start(node)
    else:
        top.start(node, (root_addr, root_port))
    simulation.topology = top
    simulation.node = node

def start_simulation(port, root_address, root_port, commands):
    simulation = Simulation(root_address, root_port)
    
    if commands is None:
        start_topology(port, root_address, root_port, simulation)
    else: # root
        start_topology(port, None, None, simulation)
    simulation.run(commands);
    
class Simulation:
    def __init__(self, root_address, root_port):
        self.node = None
        self.topology = None
        self.commands = None
        self.pending_hosts = []
        self.running_hosts = []
        self.root_address = root_address
        self.root_port = root_port
        self.lock = threading.Lock()
        self.vm_set = {}
        self.pending_vms = []
        self.sem = threading.Semaphore(0)
        self.event_queue = simulation_event_queue.SimulationEventQueue()
    
    def run(self, commands):
        self.commands = commands
        if self.commands is None: # not root
            start = message.PlatformStartedMessage()
            msg = message.SimulationMessage(start)
            id = self.topology.routing_table[self.root_address]
            if id is not None:
                self.topology.send_message(msg, id)
            self.sem.acquire()
        else: # root
            self.start_hosts(self.commands.hosts)
            self.distribute_nodes()
            print 'Node distribution: ', self.vm_set
            self.event_queue.init(self.commands.simulation.duration, self.commands.simulation.events, self.treat_simulation_event)
            self.event_queue.run()
            self.stop_hosts()
        self.topology.stop()
        
    def start_hosts(self, hosts):
        if hosts:
            print "Waiting for hosts"
            for host in hosts:
                self.pending_hosts.append(host.address)
            self.sem.acquire()
            print 'All hosts started'
        else:
            print 'No hosts expected'
        
    def stop_hosts(self):
        for host in self.running_hosts:
            stop = message.PlatformStopMessage()
            msg = message.SimulationMessage(stop)
            id = self.topology.routing_table[host]
            if id is not None:
                self.topology.send_message(msg, id)
    
    def platform_started(self, address):
        print address + ' succesfully started'
        with self.lock:
            self.running_hosts.append(address)
            self.pending_hosts.remove(address)
            if len(self.pending_hosts) is 0:
                self.sem.release()
                
    def distribute_nodes(self):
        print 'Distributing vms'
        self.pending_vms = []
        for vm in self.commands.vms:
            self.pending_vms.append(vm.name)
        self.vm_set = {}
        self.vm_to_host = {}
        for host in self.running_hosts:
            self.vm_set[host] = []
        
        # add the local node
        self.vm_set[None] = []
        # map vms to nodes
        for i in range(len(self.vm_set)):
            for j in range(i, len(self.pending_vms), len(self.vm_set)):
                if self.vm_set.keys()[i] is not  None:
                    print 'Distributing ', self.pending_vms[j], ' to ', self.vm_set.keys()[i]
                else:
                    print 'Distributing ', self.pending_vms[j], ' to local node'
                self.vm_set.values()[i].append(self.pending_vms[j])
                
        # send commands for remote nodes
        for host in self.vm_set:
            if host is not None:
                start = message.StartVmsMessage(self.vm_set[host])
                msg = message.SimulationMessage(start)
                id = self.topology.routing_table[host]
                if id is not None:
                    self.topology.send_message(msg, id)
                    for vm in self.vm_set[host]:
                        self.vm_to_host[vm] = host
                else:
                    print 'Error: Could not find host'
        
        local_vms = self.vm_set[None]
        for vm in local_vms:
            if self.start_vm(vm):
                self.vm_started(vm)
            else:
                self.stop_hosts()
                self.topology.stop()
                sys.exit(1)
            self.vm_to_host[vm] = None
        self.sem.acquire()
    
    def start_vm(self, vm):
        print 'starting ', vm
        if vm in self.topology.node.containers:
            return True
        '''
        controller = vbox_controller(vm)
        controller.lock_session()
        self.node.add_container(controller)
        controller.connect_adb()
        return True
        '''        
        if clone_vm('Android1', vm) is 0:
            controller = vbox_controller(vm)
            controller.start()
            time.sleep(60)
            controller.connect_adb()
            self.node.add_container(controller)
            return True
        else:
            return False
    
    def start_vms(self, vms, address):
        status = True
        for vm in vms:
            status = self.start_vm(vm)
            started = message.VmStartedMessage(vm, status)
            msg = message.SimulationMessage(started)
            id = self.topology.routing_table[self.root_address]
            if id is not None:
                self.topology.send_message(msg, id)
        
    def vm_started(self, vm):
        with self.lock:
            self.pending_vms.remove(vm)
            if not self.pending_vms:
                self.sem.release()
        
    def received_message(self, msg, address):
        type = message.types[msg.type]
        if type == 'PlatformStartedMessage':
            self.platform_started(address)
        elif type == 'PlatformStopMessage':
            self.sem.release()
        elif type == 'StartNodes':
            self.start_vms(msg.vms, address)
        elif type == 'VmStarted':
            if msg.status:
                self.vm_started(msg.vm)
            else:
                print "Error: Couldn't start ", msg.vm, " on ", address
        else: # default case
            pass
        
    def treat_simulation_event(self, event):
        event_type = type(event).__name__
        if event_type is 'ChangeNetworkEvent':
            self.change_network(event.vm, event.address, event.netmask)
        elif event_type is 'StopEvent':
            pass # nothing to do
        else:
            print 'Unsupported event: ', event_type
            
    def change_network(self, vm, address, netmask):
        host = self.vm_to_host[vm]
        if host is None: # local vm
            self.node.move_container_to_network(vm, address, netmask, 'root')
        else:
            id = self.topology.routing_table[host]
            if id is not None:
                msg = message.ChangeNetworkMessage(vm, address, netmask)
                self.topology.send_message(msg, id)
