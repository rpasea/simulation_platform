'''
Created on May 30, 2015

@author: radu
'''

class StopEvent(object):
    def __init__(self):
        pass
    
class ChangeNetworkEvent(object):
    def __init__(self, vm, address, netmask):
        self.vm = vm
        self.address = address
        self.netmask = netmask