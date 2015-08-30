'''
Created on May 30, 2015

@author: radu
'''

import sched, time
from simulation_platform.event_queue import simulation_events

class SimulationEventQueue:
    def __init__(self):
        self.scheduler = None
        self.start_time = None
        
    def init(self, duration, events, callback):
        self.scheduler = sched.scheduler(time.time, time.sleep)
        self.duration = duration
        for event in events:
            if event.timestamp > self.duration:
                print "Can't schedule event: ", event.__dict__
                print "Timestamp greater than duration. Discarding"
                continue
            processed_event = self.process_event(event)
            if processed_event is not None:
                self.scheduler.enter(int(event.timestamp), 1, self.event_scheduled, argument = (callback, processed_event,))
        end = simulation_events.StopEvent()
        self.scheduler.enter(self.duration, 0, self.event_scheduled, argument = (callback, end,))
    
    def run(self):
        self.start_time = time.time()
        self.scheduler.run()    
        
    def cancel(self):
        simulation_events = self.scheduler.queue()
        for event in simulation_events:
            self.scheduler.cancel(event)   
        
    def process_event(self, json_event):
        type_name = type(json_event).__name__
        if type_name is 'ChangeNetworkEvent':
            return simulation_events.ChangeNetworkEvent(json_event.vm_name, json_event.address, json_event.netmask)
        else:
            print 'Unsupported event: ', type_name
            return None
    
    def event_scheduled(self, callback, event):
        print 'Running ', type(event).__name__, ' at ', time.time() - self.start_time
        callback(event) 