from rtler_vbase import *


# TODO: figure out subclassing
class MagicMemory(ToVerilog):

  def __init__(self, num_ports, addr_sz, data_sz):
    self.wires = {}
    # Set module name
    self.name = 'MagicMemory'
    # Define ports
    self.ports = [
        VerilogPort('input', 1, 'clk'),
        VerilogPort('input', 1, 'reset'),
    ]
    for i in range(num_ports):
      # TODO: calculate correctly!
      req_sz = addr_sz + data_sz
      rsp_sz = addr_sz + data_sz
      self.ports += [
          VerilogPort('input',  req_sz, 'memreq_msg%d'%i),
          VerilogPort('input',       1, 'memreq_val%d'%i),
          VerilogPort('output',      1, 'memreq_rdy%d'%i),
          VerilogPort('output', rsp_sz, 'memrsp_msg%d'%i),
          VerilogPort('output',      1, 'memrsp_val%d'%i),
          VerilogPort('input',       1, 'memrsp_rdy%d'%i),
      ]
    for port in self.ports:
      self.__dict__[port.name] = port
    # Define modules
    self.submodules = []
    for i in range(num_ports):
      req_resp_port = FromVerilog("vgen-TestMemReqRespPort.v")
      # TODO: need different module name and instance name fields...
      req_resp_port.name = 'req_resp%d' % i
      self.submodules += [req_resp_port]
    self.wire_submodules( num_ports )

  def wire_submodules(self, num_ports):
    for i in range(num_ports):
      # TODO: won't work with multiple types of submodules...
      req_resp_port = self.submodules[i]
      req_resp_port.clk.connection   = self.clk.name
      req_resp_port.reset.connection = self.reset.name
      # Request
      req_resp_port.memreq_msg.connection = \
        self.__dict__['memreq_msg%d'%i].name
      req_resp_port.memreq_val.connection = \
        self.__dict__['memreq_val%d'%i].name
      req_resp_port.memreq_rdy.connection = \
        self.__dict__['memreq_rdy%d'%i].name
      # Response - TODO: make resp/rsp consistent
      req_resp_port.memresp_msg.connection = \
        self.__dict__['memrsp_msg%d'%i].name
      req_resp_port.memresp_val.connection = \
        self.__dict__['memrsp_val%d'%i].name
      req_resp_port.memresp_rdy.connection = \
        self.__dict__['memrsp_rdy%d'%i].name
      self.connect (
        req_resp_port.physical_block_addr_M,
        req_resp_port.physical_block_addr_M.name+str(i)
        )
      self.connect (
        req_resp_port.read_block_M,
        req_resp_port.read_block_M.name+str(i)
        )
      self.connect (
        req_resp_port.write_en_M,
        req_resp_port.write_en_M.name+str(i)
        )
      self.connect (
        req_resp_port.memreq_msg_len_modified_M,
        req_resp_port.memreq_msg_len_modified_M.name+str(i)
        )
      self.connect (
        req_resp_port.block_offset_M,
        req_resp_port.block_offset_M.name+str(i)
        )
      self.connect (
        req_resp_port.memreq_msg_data_modified_M,
        req_resp_port.memreq_msg_data_modified_M.name+str(i)
        )
      self.connect (
        req_resp_port.arb_amo_en,
        req_resp_port.arb_amo_en.name+str(i)
        )
      self.connect (
        req_resp_port.amo_grant,
        req_resp_port.amo_grant.name+str(i)
        )


  # TODO: add to verilog module baseclass? make shortcut?
  def connect(self, port, name):
    self.wires[name] = VerilogWire(name, port.width)
    port.connection = name

import unittest
class TestMagicMemory(unittest.TestCase):

  def test_one(self):
    mem_2_16_8 = MagicMemory(2,16,8)
    output = open('test.v', 'w+')
    mem_2_16_8.generate( output )
    output.close()
    import os
    cmd = 'iverilog -g2005 -Wall -I ../vc vgen-TestMemReqRespPort.v test.v'
    x = os.system(cmd)
    print cmd, x
    self.assertEqual( x, 0 )



#import sys
#output = sys.stdout
unittest.main()
