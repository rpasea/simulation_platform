import ipaddress
from bridge import bridge

class network:
    def __init__(self, address, netmask):
        self.network = ipaddress.IPv4Network(address + '/' + netmask)
        self.used_ips = []
        self.containers = {}
        self.bridge = bridge('br_' + address + '_' + netmask)

    def start(self):
        bridge_addr = self.reserve_address()
        if not bridge_addr is None:
            self.bridge.setup(str(bridge_addr), self.network.with_netmask.partition('/')[2])

    def reserve_address(self):
        for addr in self.network.hosts():
            if addr not in self.used_ips:
                self.used_ips.append(addr)
                return addr
        return None

    def attach_container(self, container):
        container_addr = self.reserve_address()
        if not container_addr is None:
            self.containers[container] = container_addr
            self.bridge.addif(container.veth_pair)
            tuple = self.network.with_netmask.partition('/')
            container.move_to_lan(str(container_addr), tuple[2], self.bridge.ip)

    def detach_container(self, container):
        if container in self.containers:
            self.bridge.delif(container.veth_pair)
            self.used_ips.remove(self.containers[container])
            del self.containers[container]
        
    def key(self):
        return self.network.with_netmask()
        
        
