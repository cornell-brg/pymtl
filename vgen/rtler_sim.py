from collections import deque
#import rtler_adder

class LogicSim():

  def __init__(self):
    self.num_cycles     = 0
    self.port_callbacks = {}
    self.event_queue    = deque()

  def cycle(self):
    self.num_cycles += 1
    while self.event_queue:
      func = self.event_queue.pop()
      func()

  def add_callback(self, port, func):
    self.port_callbacks[port] = func

  def add_event(self, port, connections):
    if port in self.port_callbacks:
      func = self.port_callbacks[port]
      if not self.event_queue or func != self.event_queue[-1]:
        self.event_queue.appendleft(func)
    for x in connections:
      if x in self.port_callbacks:
        func = self.port_callbacks[x]
        if not self.event_queue or func != self.event_queue[-1]:
          self.event_queue.appendleft(func)



