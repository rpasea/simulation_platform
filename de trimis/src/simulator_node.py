import lxc
import subprocess
from lxc_controller import lxc_controller

class InvalidOperation(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class simulator_node:
    def __init__(self):
        self.containers = {}
        # local bridges
        self.bridges = []
        self.networks = []
        self.network_to_bridge = {}

    '''
    Because we cannot add bridges to wlan interfaces, we will
    forward everything thorugh the wlan_interface.
    '''
    def setup_for_wlan_bridge(self, wlan_interface):
        subprocess.call('echo 1 > /proc/sys/net/ipv4/ip_forward', shell=True)
        subprocess.call('iptables -t nat -A POSTROUTING -o ' + wlan_interface + ' -j MASQUERADE', shell=True)

    def move_container_to_network(self, container, network):
        if container not in self.containers:
            raise InvalidOperation("Don't have container.")
        
        if network.key() in self.network_to_bridge:
            # we have a local bridge, can attach the container 
            pass
        else:
            pass

    def add_lxc(self, container_name):
        c1 = lxc_controller(container_name)
        self.containers[container_name] = c1
        
