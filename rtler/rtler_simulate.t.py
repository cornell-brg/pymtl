import unittest

from rtler_test_examples import *
from rtler_simulate import *

import rtler_debug
debug_verbose = False

class TestSlicesSim(unittest.TestCase):

  # Splitters

  def setup_splitter(self, bits, groups=None):
    if not groups:
      model = SimpleSplitter(bits)
    else:
      model = ComplexSplitter(bits, groups)
    model.elaborate()
    sim = LogicSim(model)
    sim.generate()
    if debug_verbose: rtler_debug.port_walk(model)
    return model, sim

  def verify_splitter(self, port_array, expected):
    actual = 0
    for i, port in enumerate(port_array):
      shift = i * port.width
      actual |= (port.value << shift)
    self.assertEqual( bin(actual), bin(expected) )

  def test_8_to_8x1_simplesplitter(self):
    model, sim = self.setup_splitter(8)
    model.inp.value = 0b11110000
    self.verify_splitter( model.out, 0b11110000 )

  def test_16_to_16x1_simplesplitter(self):
    model, sim = self.setup_splitter(16)
    model.inp.value = 0b11110000
    self.verify_splitter( model.out, 0b11110000 )
    model.inp.value = 0b1111000011001010
    self.verify_splitter( model.out, 0b1111000011001010 )

  def test_8_to_8x1_complexsplitter(self):
    model, sim = self.setup_splitter(8, 1)
    model.inp.value = 0b11110000
    self.verify_splitter( model.out, 0b11110000 )

  def test_8_to_4x2_complexsplitter(self):
    model, sim = self.setup_splitter(8, 2)
    model.inp.value = 0b11110000
    self.verify_splitter( model.out, 0b11110000 )

  def test_8_to_2x4_complexsplitter(self):
    model, sim = self.setup_splitter(8, 4)
    model.inp.value = 0b11110000
    self.verify_splitter( model.out, 0b11110000 )

  def test_8_to_1x8_complexsplitter(self):
    model, sim = self.setup_splitter(8, 8)
    model.inp.value = 0b11110000
    self.verify_splitter( model.out, 0b11110000 )

  # Mergers

  def setup_merger(self, bits, groups=None):
    if not groups:
      model = SimpleMerger(bits)
    else:
      model = ComplexMerger(bits, groups)
    model.elaborate()
    sim = LogicSim(model)
    sim.generate()
    return model, sim

  def set_ports(self, port_array, value):
    for i, port in enumerate(port_array):
      shift = i * port.width
      port.value = (value >> shift)

  def test_8x1_to_8_simplemerger(self):
    model, sim = self.setup_merger(8)
    self.set_ports( model.inp, 0b11110000 )
    self.assertEqual( model.out.value, 0b11110000 )

  def test_16x1_to_16_simplemerger(self):
    model, sim = self.setup_merger(16)
    self.set_ports( model.inp, 0b11110000 )
    self.assertEqual( model.out.value, 0b11110000 )
    self.set_ports( model.inp, 0b1111000011001010 )
    self.assertEqual( model.out.value, 0b1111000011001010 )

  def test_8x1_to_8_complexmerger(self):
    model, sim = self.setup_merger(8, 1)
    self.set_ports( model.inp, 0b11110000 )
    self.assertEqual( model.out.value, 0b11110000 )

  def test_4x2_to_8_complexmerger(self):
    model, sim = self.setup_merger(8, 2)
    self.set_ports( model.inp, 0b11110000 )
    self.assertEqual( model.out.value, 0b11110000 )

  def test_2x4_to_8_complexmerger(self):
    model, sim = self.setup_merger(8, 4)
    self.set_ports( model.inp, 0b11110000 )
    self.assertEqual( model.out.value, 0b11110000 )

  def test_1x8_to_8_complexmerger(self):
    model, sim = self.setup_merger(8, 8)
    self.set_ports( model.inp, 0b11110000 )
    self.assertEqual( model.out.value, 0b11110000 )



#class RegisteredAdder1(VerilogModule):
#  def __init__(self, bits):
#    self.in0 = InPort(bits)
#    self.in1 = InPort(bits)
#    self.out = OutPort(bits)
#  @rising_edge
#  def tick(self):
#    in0 = self.in0
#    in1 = self.in1
#    out = self.out
#    out <<= in0 + in1
#
#class RegisteredAdder2(VerilogModule):
#  def __init__(self, bits):
#    self.in0 = InPort(bits)
#    self.in1 = InPort(bits)
#    self.out = OutPort(bits)
#    self.sum = Wire(bits)
#  @combinational
#  def tick(self):
#    in0 = self.in0
#    in1 = self.in1
#    sum = self.sum
#    sum <<= in0 + in1
#  @rising_edge
#  def tick():
#    in0 = self.in0
#    in1 = self.in1
#    out = self.out
#    out <<= sum


class TestRisingEdge(unittest.TestCase):

  def setup_sim(self, model):
    model.elaborate()
    sim = LogicSim(model)
    sim.generate()
    import rtler_debug
    if debug_verbose: rtler_debug.port_walk(model)
    return sim

  def test_wire(self):
    model = Wire(16)
    sim = self.setup_sim(model)
    model.inp.value = 8
    self.assertEqual( model.out.value, 8)
    model.inp.value = 9
    model.inp.value = 10
    self.assertEqual( model.out.value, 10)

  def test_wire_wrapped(self):
    model = WireWrapped(16)
    sim = self.setup_sim(model)
    model.inp.value = 8
    self.assertEqual( model.out.value, 8)
    model.inp.value = 9
    model.inp.value = 10
    self.assertEqual( model.out.value, 10)

  def test_register(self):
    model = Register(16)
    sim = self.setup_sim(model)
    model.inp.value = 8
    self.assertEqual( model.out.value, 0)
    sim.cycle()
    self.assertEqual( model.out.value, 8)
    model.inp.value = 9
    self.assertEqual( model.out.value, 8)
    model.inp.value = 10
    sim.cycle()
    self.assertEqual( model.out.value, 10)

  def test_register_wrapped(self):
    model = RegisterWrapper(16)
    sim = self.setup_sim(model)
    model.inp.value = 8
    self.assertEqual( model.out.value, 0)
    sim.cycle()
    self.assertEqual( model.out.value, 8)
    model.inp.value = 9
    self.assertEqual( model.out.value, 8)
    model.inp.value = 10
    sim.cycle()
    self.assertEqual( model.out.value, 10)

  def test_register_chain(self):
    model = RegisterChain(16)
    sim = self.setup_sim(model)
    model.inp.value = 8
    self.assertEqual( model.reg1.out.value, 0)
    self.assertEqual( model.reg2.out.value, 0)
    self.assertEqual( model.reg3.out.value, 0)
    self.assertEqual( model.out.value,      0)
    sim.cycle()
    self.assertEqual( model.reg1.out.value, 8)
    self.assertEqual( model.reg2.out.value, 0)
    self.assertEqual( model.reg3.out.value, 0)
    self.assertEqual( model.out.value,      0)
    model.inp.value = 9
    self.assertEqual( model.reg1.out.value, 8)
    self.assertEqual( model.reg2.out.value, 0)
    self.assertEqual( model.reg3.out.value, 0)
    self.assertEqual( model.out.value,      0)
    model.inp.value = 10
    sim.cycle()
    self.assertEqual( model.reg1.out.value,10)
    self.assertEqual( model.reg2.out.value, 8)
    self.assertEqual( model.reg3.out.value, 0)
    self.assertEqual( model.out.value,      0)
    sim.cycle()
    self.assertEqual( model.reg1.out.value,10)
    self.assertEqual( model.reg2.out.value,10)
    self.assertEqual( model.reg3.out.value, 8)
    self.assertEqual( model.out.value,      8)
    sim.cycle()
    self.assertEqual( model.reg1.out.value,10)
    self.assertEqual( model.reg2.out.value,10)
    self.assertEqual( model.reg3.out.value,10)
    self.assertEqual( model.out.value,     10)

  def verify_splitter(self, port_array, expected):
    actual = 0
    for i, port in enumerate(port_array):
      shift = i * port.width
      actual |= (port.value << shift)
    self.assertEqual( bin(actual), bin(expected) )

  def test_register_splitter(self):
    model = RegisterSplitter(16)
    sim = self.setup_sim(model)
    model.inp.value = 0b11110000
    self.verify_splitter( model.out, 0b0 )
    self.assertEqual( model.reg.out.value, 0b0 )
    sim.cycle()
    self.assertEqual( model.reg.out.value, 0b11110000 )
    self.assertEqual( model.split.inp.value, 0b11110000 )
    self.verify_splitter( model.split.out, 0b11110000 )
    self.verify_splitter( model.out, 0b11110000 )
    model.inp.value = 0b1111000011001010
    self.assertEqual( model.reg.out.value, 0b11110000 )
    self.assertEqual( model.split.inp.value, 0b11110000 )
    self.verify_splitter( model.split.out, 0b11110000 )
    self.verify_splitter( model.out, 0b11110000 )
    sim.cycle()
    self.assertEqual( model.reg.out.value, 0b1111000011001010 )
    self.verify_splitter( model.out, 0b1111000011001010 )

if __name__ == '__main__':
  unittest.main()
