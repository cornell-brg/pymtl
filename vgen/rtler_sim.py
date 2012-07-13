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

  def add_event(self, port1, port2):
    if port1 in self.port_callbacks:
      func1 = self.port_callbacks[port1]
      if not self.event_queue or func1 != self.event_queue[-1]:
        self.event_queue.appendleft(func1)
    if port2 in self.port_callbacks:
      func2 = self.port_callbacks[port2]
      if not self.event_queue or func2 != self.event_queue[-1]:
        self.event_queue.appendleft(func2)



