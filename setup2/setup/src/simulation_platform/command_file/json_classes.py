'''
Created on May 16, 2015

@author: radu
'''
import jsonpickle

def to_json(obj):
    jsonpickle.set_encoder_options('json', sort_keys=True, indent=4, separators=(',', ': '))
    return jsonpickle.encode(obj)

def from_json(string):
    return jsonpickle.decode(string)

class Host(object):
    def __init__(self, address = None, port = None):
        self.port = port
        self.address = address
        
class AndroidVM(object):
    def __init__(self, name = None):
        self.name = name
        
class ChangeNetworkEvent(object):
    def __init__(self, vm_name = None, address = None, netmask = None, timestamp = None):
        self.vm_name = vm_name
        self.address = address
        self.netmask = netmask
        self.timestamp = timestamp

class Simulation(object):
    def __init__(self, duration = None, events = None):
        self.duration = duration
        if events is not None:
            self.events = events
        else:
            self.events = []

class CommandFile(object):
    def __init__(self):
        self.hosts = []
        self.vms = []
        self.simulation = None
        #self.path = 'proiect_disertatie/proiect/start.py'