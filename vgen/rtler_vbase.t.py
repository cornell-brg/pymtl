from rtler_vbase import *


# TODO: figure out subclassing
class MagicMemory(ToVerilog):

  def __init__(self, num_ports, addr_sz, data_sz):
    # Set module name
    self.name = 'MagicMemory'
    # Define ports
    self.ports = [
        TempPort('input', 1, 'clk'),
        TempPort('input', 1, 'reset'),
    ]
    for i in range(num_ports):
      # TODO: calculate correctly!
      req_sz = addr_sz + data_sz
      rsp_sz = addr_sz + data_sz
      self.ports += [
          TempPort('input',  req_sz, 'memreq_msg%d'%i),
          TempPort('input',       1, 'memreq_val%d'%i),
          TempPort('output',      1, 'memreq_rdy%d'%i),
          TempPort('output', rsp_sz, 'memrsp_msg%d'%i),
          TempPort('output',      1, 'memrsp_val%d'%i),
          TempPort('input',       1, 'memrsp_rdy%d'%i),
      ]
    for port in self.ports:
      self.__dict__[port.name] = port



mem_1_8_8 = MagicMemory(1,8,8)
#print mem_1_8_8
#print mem_1_8_8.ports

mem_2_16_8 = MagicMemory(2,16,8)
#print mem_2_16_8
#print mem_2_16_8.ports

mem_8_32_32 = MagicMemory(8,32,32)
print mem_8_32_32
print mem_8_32_32.ports
print mem_8_32_32.memrsp_rdy7
#import sys
#output = sys.stdout
#import StringIO
#output = StringIO.StringIO()
fd = open('test.v', 'w')
output = fd
mem_8_32_32.generate( output )

