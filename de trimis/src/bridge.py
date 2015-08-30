import subprocess

class bridge:
    def __init__(self, name):
        self.name = name
        self.ip = ''
        self.netmask = ''

    def setup(self, ip, netmask):
        subprocess.call('brctl addbr ' + self.name, shell=True)
        subprocess.call('ifconfig ' + self.name + ' ' + ip + ' netmask ' + netmask + ' up', shell=True)
        self.ip = ip
        self.netmask = netmask

    def addif(self, interface):
        subprocess.call('brctl addif ' + self.name + ' ' + interface, shell=True)

    def delif(self, interface):
        subprocess.call('brctl delif ' + self.name + ' ' + interface, shell=True)
        
