import unittest
import sys
import os

from test_examples import *
from translate     import *

import debug_utils
debug_verbose = False

import pytest

class TestSlicesVerilog(unittest.TestCase):

  def setUp(self):
    self.temp_file = self.id().split('.')[-1] + '.v'
    self.fd = open(self.temp_file, 'w')
    self.compile_cmd = ("iverilog -g2005 -Wall -Wno-sensitivity-entire-vector"
                        "-Wno-sensitivity-entire-array " + self.temp_file)

  def translate(self, model):
    model.elaborate()
    if debug_verbose: debug_utils.port_walk(model)
    code = VerilogTranslationTool(model, self.fd)
    #code.translate( self.fd )
    self.fd.close()

  def test_rotator(self):
    self.translate( Rotator(8) )
    x = os.system( self.compile_cmd )
    self.assertEqual( x, 0)

  def test_simplesplitter(self):
    self.translate( SimpleSplitter(8) )
    x = os.system( self.compile_cmd )
    self.assertEqual( x, 0)

  def test_simplemerger(self):
    self.translate( SimpleMerger(8) )
    x = os.system( self.compile_cmd )
    self.assertEqual( x, 0)

  def test_complexsplitter(self):
    self.translate( ComplexSplitter(16, 4) )
    x = os.system( self.compile_cmd )
    self.assertEqual( x, 0)

  def test_complexmerger(self):
    self.translate( ComplexMerger(16, 4) )
    x = os.system( self.compile_cmd )
    self.assertEqual( x, 0)

  def test_signext_slice(self):
    self.translate( SignExtSlice(4) )
    x = os.system( self.compile_cmd )
    self.assertEqual( x, 0)

  # TODO: Add this back in? -cbatten
  #def test_signext_comb(self):
  #  self.translate( SignExtComb(4) )
  #  x = os.system( self.compile_cmd )
  #  self.assertEqual( x, 0)

  #def tearDown(self):
  #  os.remove(self.temp_file)


class TestCombinationalVerilog(unittest.TestCase):

  def setUp(self):
    self.temp_file = self.id().split('.')[-1] + '.v'
    self.fd = open(self.temp_file, 'w')
    self.compile_cmd = ("iverilog -g2005 -Wall -Wno-sensitivity-entire-vector"
                        "-Wno-sensitivity-entire-array " + self.temp_file)

  def translate(self, model):
    model.elaborate()
    if debug_verbose: debug_utils.port_walk(model)
    code = VerilogTranslationTool( model, self.fd )
    #code.translate( self.fd )
    self.fd.close()

  def test_onewire(self):
    model = OneWire(16)
    self.translate( model )
    x = os.system( self.compile_cmd )
    self.assertEqual( x, 0)

  def test_onewire_wrapped(self):
    model = OneWireWrapped(16)
    self.translate( model )
    x = os.system( self.compile_cmd )
    self.assertEqual( x, 0)

  def test_full_adder(self):
    model = FullAdder()
    self.translate( model )
    x = os.system( self.compile_cmd )
    self.assertEqual( x, 0)

  def test_ripple_carry(self):
    model = RippleCarryAdder(4)
    self.translate( model )
    x = os.system( self.compile_cmd )
    self.assertEqual( x, 0)

  #def tearDown(self):
  #  os.remove(self.temp_file)


class TestPosedgeClkVerilog(unittest.TestCase):

  def setUp(self):
    self.temp_file = self.id().split('.')[-1] + '.v'
    self.fd = open(self.temp_file, 'w')
    self.compile_cmd = ("iverilog -g2005 -Wall -Wno-sensitivity-entire-vector"
                        "-Wno-sensitivity-entire-array " + self.temp_file)

  def translate(self, model):
    model.elaborate()
    if debug_verbose: debug_utils.port_walk(model)
    code = VerilogTranslationTool( model, self.fd )
    #code.translate( self.fd )
    self.fd.close()

  def test_register(self):
    model = Register(16)
    self.translate( model )
    x = os.system( self.compile_cmd )
    self.assertEqual( x, 0)

  def test_register_reset(self):
    model = RegisterReset(16)
    self.translate( model )
    x = os.system( self.compile_cmd )
    self.assertEqual( x, 0)

  def test_register_wrapped(self):
    model = RegisterWrapper(16)
    self.translate( model )
    x = os.system( self.compile_cmd )
    self.assertEqual( x, 0)

  def test_register_chain(self):
    model = RegisterChain(16)
    self.translate( model )
    x = os.system( self.compile_cmd )
    self.assertEqual( x, 0)

  def test_register_splitter(self):
    model = RegisterSplitter(16)
    self.translate( model )
    x = os.system( self.compile_cmd )
    self.assertEqual( x, 0)

  def test_fanout_one(self):
    model = FanOutOne(16)
    self.translate( model )
    x = os.system( self.compile_cmd )
    self.assertEqual( x, 0)

  def test_fanout_two(self):
    model = FanOutTwo(16)
    self.translate( model )
    x = os.system( self.compile_cmd )
    self.assertEqual( x, 0)

  #def tearDown(self):
  #  os.remove(self.temp_file)

class TestCombAndPosedgeVerilog(unittest.TestCase):

  def setUp(self):
    self.temp_file = self.id().split('.')[-1] + '.v'
    self.fd = open(self.temp_file, 'w')
    self.compile_cmd = ("iverilog -g2005 -Wall -Wno-sensitivity-entire-vector"
                        "-Wno-sensitivity-entire-array " + self.temp_file)

  def translate(self, model):
    model.elaborate()
    if debug_verbose: debug_utils.port_walk(model)
    code = VerilogTranslationTool(model)
    code = VerilogTranslationTool( model, self.fd )
    #code.translate( self.fd )
    self.fd.close()

  def test_incrementer(self):
    model = Incrementer()
    self.translate( model )
    x = os.system( self.compile_cmd )
    self.assertEqual( x, 0)

  def test_counter(self):
    model = Counter(7)
    self.translate( model )
    x = os.system( self.compile_cmd )
    self.assertEqual( x, 0)

  def test_count_incr(self):
    model = CountIncr(7)
    self.translate( model )
    x = os.system( self.compile_cmd )
    self.assertEqual( x, 0)

  def test_reg_incr(self):
    model = RegIncr()
    self.translate( model )
    x = os.system( self.compile_cmd )
    self.assertEqual( x, 0)

  def test_incr_reg(self):
    model = IncrReg()
    self.translate( model )
    x = os.system( self.compile_cmd )
    self.assertEqual( x, 0)

  def test_incr_reg(self):
    model = IncrReg()
    self.translate( model )
    x = os.system( self.compile_cmd )
    self.assertEqual( x, 0)

  # TODO: add this back in? -cbatten
  # def test_gcd(self):
  #   model = GCD()
  #   self.translate( model )
  #   x = os.system( self.compile_cmd )
  #   self.assertEqual( x, 0)

  #def tearDown(self):
  #  os.remove(self.temp_file)


class DumbA(Model):
  def __init__(self):
    self.in_A  = InPort(1)
    self.in_B  = InPort(1)
    self.in_C  = InPort(1)
    self.in_D  = InPort(1)
    self.out_A = OutPort(1)
    self.out_B = OutPort(1)
    self.out_C = OutPort(1)
    self.out_D = OutPort(1)
  @posedge_clk
  def tick(self):
    if in_A:
      self.out_A.next = 5
    else:
      if in_B:
        self.out_B.next = 5
      elif in_C:
        self.out_C.next = 5
      if in_D:
        self.out_D.next = 5

class DumbB(Model):
  def __init__(self):
    self.in_A  = InPort(1)
    self.in_B  = InPort(1)
    self.in_C  = InPort(1)
    self.in_D  = InPort(1)
    self.in_E  = InPort(1)
    self.in_X  = InPort(1)
    self.in_Y  = InPort(1)
    self.out_A = OutPort(1)
    self.out_B = OutPort(1)
    self.out_C = OutPort(1)
    self.out_D = OutPort(1)
    self.out_E = OutPort(1)
    self.out_X = OutPort(1)
    self.out_Y = OutPort(1)
  @posedge_clk
  def tick(self):
    if in_A:
      self.out_A.next = 5
    elif in_E:
      self.out_E.next = 5
    else:
      self.out_X.next = 10
      self.out_Y.next = 10
      if in_B:
        self.out_B.next = 5
        self.out_X.next = 5
      elif in_C:
        self.out_C.next = 5
      elif in_D:
        self.out_D.next = 5
      else:
        if in_A:
          self.out_A.next = 5
        elif in_C:
          self.out_C.next = 5
        elif in_D:
          self.out_D.next = 5
        else:
          self.out_E.next = 5

        if in_A:
          self.out_A.next = 5
        elif in_C:
          self.out_C.next = 5
        elif in_D:
          self.out_D.next = 5
        else:
          self.out_E.next = 5

class FixCompare(Model):
  def __init__(self):
    self.clear        = InPort( 1 )
    self.p_data_nbits = 4
    self.count        = OutPort( self.p_data_nbits )
    self.c_max_value  = 2**self.p_data_nbits
  @posedge_clk
  def seq_logic( self ):
    if ( self.clear.value ):
      self.count.next = 0
    elif ( self.count.value == self.c_max_value - 1 ):
      self.count.next = 0
    else:
      self.count.next = self.count.value + 1


class TestDumb(unittest.TestCase):

  def setUp(self):
    self.temp_file = self.id().split('.')[-1] + '.v'
    self.fd = open(self.temp_file, 'w')
    self.compile_cmd = ("iverilog -g2005 -Wall -Wno-sensitivity-entire-vector"
                        "-Wno-sensitivity-entire-array " + self.temp_file)

  def translate(self, model):
    model.elaborate()
    if debug_verbose: debug_utils.port_walk(model)
    code = VerilogTranslationTool( model, self.fd )
    #code.translate( self.fd )
    self.fd.close()

  def test_dumb_a(self):
    model = DumbA()
    self.translate( model )
    x = os.system( self.compile_cmd )
    self.assertEqual( x, 0)

  def test_dumb_b(self):
    model = DumbB()
    self.translate( model )
    x = os.system( self.compile_cmd )
    self.assertEqual( x, 0)

  def test_fix_compare(self):
    model = FixCompare()
    self.translate( model )
    x = os.system( self.compile_cmd )
    self.assertEqual( x, 0)

  def test_mux_register(self):
    model = MuxRegister( 3, 8 )
    self.translate( model )
    x = os.system( self.compile_cmd )
    self.assertEqual( x, 0)

  def test_demux_no_loop(self):
    model = DemuxNoLoop( 3, 8 )
    self.translate( model )
    x = os.system( self.compile_cmd )
    self.assertEqual( x, 0)

  def test_demux(self):
    model = Demux( 3, 8 )
    self.translate( model )
    x = os.system( self.compile_cmd )
    self.assertEqual( x, 0)


if __name__ == '__main__':
  unittest.main()
