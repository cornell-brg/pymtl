import unittest
import sys

from rtler_test_examples import *
from rtler_translate import *

import rtler_debug
debug_verbose = False

class TestSlicesVerilog(unittest.TestCase):

  def translate(self, model):
    model.elaborate()
    if debug_verbose: rtler_debug.port_walk(model)
    code = ToVerilog(model)
    code.generate( sys.stdout )

  #TODO: how do we test this?!
  def test_rotator(self):
    self.translate( Rotator(8) )

  def test_simplesplitter(self):
    self.translate( SimpleSplitter(8) )

  def test_simplemerger(self):
    self.translate( SimpleMerger(8) )

  def test_complexsplitter(self):
    self.translate( ComplexSplitter(16, 4) )

  def test_complexmerger(self):
    self.translate( ComplexMerger(16, 4) )

  def test_wire(self):
    model = Wire(16)
    self.translate( model )

  def test_wire_wrapped(self):
    model = WireWrapped(16)
    self.translate( model )

  def test_register(self):
    model = Register(16)
    self.translate( model )

  def test_register_wrapped(self):
    model = RegisterWrapper(16)
    self.translate( model )

  def test_register_chain(self):
    model = RegisterChain(16)
    self.translate( model )

  def test_register_splitter(self):
    model = RegisterSplitter(16)
    self.translate( model )

if __name__ == '__main__':
  unittest.main()
