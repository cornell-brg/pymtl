import unittest

from pymtl_test_examples import *
from pymtl_simulate import *

import pymtl_debug
debug_verbose = False

class TestNode(unittest.TestCase):

  def setUp(self):
    self.reg = Node(8)
    sim = LogicSim(None)
    self.reg.sim = sim

  def test_init_write(self):
    self.reg.next = 2
    self.assertEqual( self.reg.value, 0 )
    self.reg.clock()
    self.assertEqual( self.reg.value, 2 )

  def test_second_write(self):
    self.reg.next = 5
    self.reg.clock()
    self.reg.next = 7
    self.reg.next = 8
    self.assertEqual( self.reg.value, 5 )
    self.reg.clock()
    self.assertEqual( self.reg.value, 8 )


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
    #if debug_verbose: rtler_debug.port_walk(model)
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


class TestCombinationalSim(unittest.TestCase):

  def setup_sim(self, model):
    model.elaborate()
    sim = LogicSim(model)
    sim.generate()
    if debug_verbose:
      pymtl_debug.port_walk(model)
    return sim

  def test_onewire(self):
    model = OneWire(16)
    sim = self.setup_sim(model)
    model.inp.value = 8
    # Note: no need to call cycle, no @combinational block
    self.assertEqual( model.out.value, 8)
    model.inp.value = 9
    model.inp.value = 10
    self.assertEqual( model.out.value, 10)

  def test_onewire_wrapped(self):
    model = OneWireWrapped(16)
    sim = self.setup_sim(model)
    model.inp.value = 8
    # Note: no need to call cycle, no @combinational block
    self.assertEqual( model.out.value, 8)
    model.inp.value = 9
    model.inp.value = 10
    self.assertEqual( model.out.value, 10)

  def test_full_adder(self):
    model = FullAdder()
    sim = self.setup_sim(model)
    import itertools
    for x,y,z in itertools.product([0,1], [0,1], [0,1]):
      model.in0.value = x
      model.in1.value = y
      model.cin.value = z
      sim.cycle()
      self.assertEqual( model.sum.value,  x^y^z )
      self.assertEqual( model.cout.value, (x&y)|(x&z)|(y&z) )

  def test_ripple_carry(self):
    model = RippleCarryAdder(4)
    sim = self.setup_sim(model)
    model.in0.value = 2
    model.in1.value = 2
    sim.cycle()
    self.assertEqual( model.sum.value, 4 )
    model.in0.value = 11
    model.in1.value = 4
    sim.cycle()
    self.assertEqual( model.sum.value, 15 )
    model.in0.value = 9
    self.assertEqual( model.sum.value, 15 )
    sim.cycle()
    self.assertEqual( model.sum.value, 13 )
    model.in0.value = 5
    model.in1.value = 12
    self.assertEqual( model.sum.value, 13 )
    sim.cycle()
    self.assertEqual( model.sum.value, 1 )

  def test_ripple_carry(self):
    model = RippleCarryAdder(4)
    sim = self.setup_sim(model)


class TestPosedgeClkSim(unittest.TestCase):

  def setup_sim(self, model):
    model.elaborate()
    sim = LogicSim(model)
    sim.generate()
    if debug_verbose:
      pymtl_debug.port_walk(model)
    return sim

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
    self.assertEqual( model.reg0.out.value, 0b0 )
    sim.cycle()
    self.assertEqual( model.reg0.out.value, 0b11110000 )
    self.assertEqual( model.split.inp.value, 0b11110000 )
    self.verify_splitter( model.split.out, 0b11110000 )
    self.verify_splitter( model.out, 0b11110000 )
    model.inp.value = 0b1111000011001010
    self.assertEqual( model.reg0.out.value, 0b11110000 )
    self.assertEqual( model.split.inp.value, 0b11110000 )
    self.verify_splitter( model.split.out, 0b11110000 )
    self.verify_splitter( model.out, 0b11110000 )
    sim.cycle()
    self.assertEqual( model.reg0.out.value, 0b1111000011001010 )
    self.verify_splitter( model.out, 0b1111000011001010 )

class TestCombAndPosedge(unittest.TestCase):

  def setup_sim(self, model):
    model.elaborate()
    sim = LogicSim(model)
    sim.generate()
    if debug_verbose:
      pymtl_debug.port_walk(model)
    return sim

  def test_incrementer(self):
    model = Incrementer()
    sim = self.setup_sim(model)
    model.inp.value = 8
    self.assertEqual( model.out.value, 0)
    for i in xrange(10):
      model.inp.value = i
      sim.cycle()
      self.assertEqual( model.out.value, i+1)

  def test_counter(self):
    model = Counter(7)
    sim = self.setup_sim(model)
    model.clear.value = 0
    self.assertEqual( model.count.value, 0)
    expected = [1,2,3,4,5,6,7,0,1,2,
                0,1,2,3,4,5,6,7,0,1]
    for i in xrange(20):
      if i == 10:
        model.clear.value = 1
      else:
        model.clear.value = 0
      sim.cycle()
      self.assertEqual( model.count.value, expected[i])

  def test_count_incr(self):
    model = CountIncr(7)
    sim = self.setup_sim(model)
    model.clear.value = 0
    self.assertEqual( model.count.value, 0)
    expected = [1,2,3,4,5,6,7,0,1,2,
                0,1,2,3,4,5,6,7,0,1]
    for i in xrange(20):
      if i == 10:
        model.clear.value = 1
      else:
        model.clear.value = 0
      sim.cycle()
      self.assertEqual( model.count.value, expected[i]+1)

  def test_reg_incr(self):
    model = RegIncr()
    sim = self.setup_sim(model)
    model.inp.value = 8
    self.assertEqual( model.out.value, 0)
    for i in xrange(20):
      model.inp.value = i
      sim.cycle()
      self.assertEqual( model.out.value, i+1)

  def test_incr_reg(self):
    model = IncrReg()
    sim = self.setup_sim(model)
    model.inp.value = 8
    self.assertEqual( model.out.value, 0)
    for i in xrange(20):
      model.inp.value = i
      sim.cycle()
      self.assertEqual( model.out.value, i+1)

if __name__ == '__main__':
  unittest.main()
