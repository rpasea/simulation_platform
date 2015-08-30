import lxc

class lxc_controller:
    def __init__(self, name):
        self.container = lxc.Container(name)
        self.veth_pair = self.container.get_config_item('lxc.network.0.veth.pair')

    def start(self):
        self.container.start()

    def stop(self):
        if not self.container.shutdown(5):
            self.container.stop()

    def move_to_lan(self, ip, netmask, gateway):
        self.container.attach_wait(lxc.attach_run_command,
                                   ['ifconfig', 'eth0', ip, 'netmask', netmask, 'up'])
        self.container.attach_wait(lxc.attach_run_command,
                                   ['route', 'add', 'default', 'gw', gateway, 'eth0'])
        
        self.container.attach_wait(lxc.attach_run_command, 'ifconfig')
