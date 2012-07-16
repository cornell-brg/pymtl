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
    # TODO: doesnt' work in __init__ because ValueNodes are not
    #       created until elaborate!
    #node = port._value
    #print "ADDCALLBACK:", port.name, node
    ## TODO: might need to support multiple funcs?
    #self.port_callbacks[node] = func
    port.funcs.add( func )

  def add_event(self, port, connections):
    node = port._value
    for func in node.funcs:
      if func not in self.event_queue:
        #print "ADDEVENT:", port.parent, port.name, port.value, func
        self.event_queue.appendleft(func)


