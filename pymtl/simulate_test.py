import unittest

from test_examples import *
from simulate import *

import debug_utils
debug_verbose = True


class TestSlicesSim(unittest.TestCase):

  # Splitters
  def setup_sim(self, model):
    model.elaborate()
    sim = SimulationTool(model)
    if debug_verbose:
      debug_utils.port_walk(model)
    return sim

  def setup_splitter(self, bits, groups=None):
    if not groups:
      model = SimpleSplitter(bits)
    else:
      model = ComplexSplitter(bits, groups)
    sim = self.setup_sim(model)
    return model, sim

  def verify_splitter(self, port_array, expected):
    actual = 0
    for i, port in enumerate(port_array):
      shift = i * port.width
      print port.value
      actual |= (port.value.uint << shift)
    self.assertEqual( bin(actual), bin(expected) )

  def test_8_to_8x1_simplesplitter(self):
    model, sim = self.setup_splitter(8)
    model.inp.value = 0b11110000
    print model.inp.value
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
    sim = self.setup_sim(model)
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

  # Bit Repeat

  def test_signext_slice( self ):
    model = SignExtSlice( 2 )
    sim = self.setup_sim(model)
    #debug_utils.port_walk( model )
    #import visualize
    #viz = visualize.VisualizationTool( model )
    #viz.generate()
    #viz.to_diagram( '_temp.png')
    test_cases = [ [ 0, 0,],
                   [ 1, 3,],
                 ]
    for test in test_cases:
      model.in_.value = test[0]
      print bin(model.out.value.uint), model.out[1].value, model.out[0].value
      self.assertEquals( model.out.value, test[1] )

  def test_signext_comb( self ):
    model = SignExtComb( 2 )
    sim = self.setup_sim(model)
    print sim.vnode_callbacks
    test_cases = [ [ 0, 0,],
                   [ 1, 3,],
                 ]
    for test in test_cases:
      model.in_.value = test[0]
      print bin(model.out.value.uint), model.out[1].value, model.out[0].value
      sim.cycle()
      self.assertEquals( model.out.value, test[1] )


class TestCombinationalSim(unittest.TestCase):

  def setup_sim(self, model):
    model.elaborate()
    sim = SimulationTool(model)
    if debug_verbose:
      debug_utils.port_walk(model)
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
    model.inp.value = -1
    self.assertEqual( model.out.value, 65535)

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
    sim.reset()
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
    sim.reset()
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


#class TestPosedgeClkSim(unittest.TestCase):
#
#  def setup_sim(self, model):
#    model.elaborate()
#    sim = SimulationTool(model)
#    if debug_verbose:
#      debug_utils.port_walk(model)
#    return sim
#
#  def test_register(self):
#    model = Register(16)
#    sim = self.setup_sim(model)
#    model.inp.value = 8
#    self.assertEqual( model.out.value, 0)
#    sim.cycle()
#    self.assertEqual( model.out.value, 8)
#    model.inp.value = 9
#    self.assertEqual( model.out.value, 8)
#    model.inp.value = 10
#    sim.cycle()
#    self.assertEqual( model.out.value, 10)
#    model.inp.value = -1
#    sim.cycle()
#    self.assertEqual( model.out.value, 65535)
#
#  def test_register_reset(self):
#    model = RegisterReset(16)
#    sim = self.setup_sim(model)
#    model.inp.value = 8
#    self.assertEqual( model.out.value, 0)
#    sim.reset()
#    self.assertEqual( model.out.value, 0)
#    sim.cycle()
#    self.assertEqual( model.out.value, 8)
#    model.inp.value = 9
#    self.assertEqual( model.out.value, 8)
#    model.inp.value = 10
#    sim.cycle()
#    self.assertEqual( model.out.value, 10)
#    sim.reset()
#    self.assertEqual( model.out.value, 0)
#
#  def test_register_wrapped(self):
#    model = RegisterWrapper(16)
#    sim = self.setup_sim(model)
#    sim.reset()
#    model.inp.value = 8
#    self.assertEqual( model.out.value, 0)
#    sim.cycle()
#    self.assertEqual( model.out.value, 8)
#    model.inp.value = 9
#    self.assertEqual( model.out.value, 8)
#    model.inp.value = 10
#    sim.cycle()
#    self.assertEqual( model.out.value, 10)
#
#  def test_register_chain(self):
#    model = RegisterChain(16)
#    sim = self.setup_sim(model)
#    sim.reset()
#    model.inp.value = 8
#    self.assertEqual( model.reg1.out.value, 0)
#    self.assertEqual( model.reg2.out.value, 0)
#    self.assertEqual( model.reg3.out.value, 0)
#    self.assertEqual( model.out.value,      0)
#    sim.cycle()
#    self.assertEqual( model.reg1.out.value, 8)
#    self.assertEqual( model.reg2.out.value, 0)
#    self.assertEqual( model.reg3.out.value, 0)
#    self.assertEqual( model.out.value,      0)
#    model.inp.value = 9
#    self.assertEqual( model.reg1.out.value, 8)
#    self.assertEqual( model.reg2.out.value, 0)
#    self.assertEqual( model.reg3.out.value, 0)
#    self.assertEqual( model.out.value,      0)
#    model.inp.value = 10
#    sim.cycle()
#    self.assertEqual( model.reg1.out.value,10)
#    self.assertEqual( model.reg2.out.value, 8)
#    self.assertEqual( model.reg3.out.value, 0)
#    self.assertEqual( model.out.value,      0)
#    sim.cycle()
#    self.assertEqual( model.reg1.out.value,10)
#    self.assertEqual( model.reg2.out.value,10)
#    self.assertEqual( model.reg3.out.value, 8)
#    self.assertEqual( model.out.value,      8)
#    sim.cycle()
#    self.assertEqual( model.reg1.out.value,10)
#    self.assertEqual( model.reg2.out.value,10)
#    self.assertEqual( model.reg3.out.value,10)
#    self.assertEqual( model.out.value,     10)
#
#  def verify_splitter(self, port_array, expected):
#    actual = 0
#    for i, port in enumerate(port_array):
#      shift = i * port.width
#      actual |= (port.value << shift)
#    self.assertEqual( bin(actual), bin(expected) )
#
#  def test_register_splitter(self):
#    model = RegisterSplitter(16)
#    sim = self.setup_sim(model)
#    sim.reset()
#    model.inp.value = 0b11110000
#    self.verify_splitter( model.out, 0b0 )
#    self.assertEqual( model.reg0.out.value, 0b0 )
#    sim.cycle()
#    self.assertEqual( model.reg0.out.value, 0b11110000 )
#    self.assertEqual( model.split.inp.value, 0b11110000 )
#    self.verify_splitter( model.split.out, 0b11110000 )
#    self.verify_splitter( model.out, 0b11110000 )
#    model.inp.value = 0b1111000011001010
#    self.assertEqual( model.reg0.out.value, 0b11110000 )
#    self.assertEqual( model.split.inp.value, 0b11110000 )
#    self.verify_splitter( model.split.out, 0b11110000 )
#    self.verify_splitter( model.out, 0b11110000 )
#    sim.cycle()
#    self.assertEqual( model.reg0.out.value, 0b1111000011001010 )
#    self.verify_splitter( model.out, 0b1111000011001010 )
#
#  def test_fanout_one(self):
#    model = FanOutOne(16)
#    sim = self.setup_sim(model)
#    sim.reset()
#    model.inp.value = 8
#    self.assertEqual( model.reg0.out.value,  0)
#    self.assertEqual( model.out1.value,      0)
#    self.assertEqual( model.out2.value,      0)
#    self.assertEqual( model.out3.value,      0)
#    sim.cycle()
#    self.assertEqual( model.reg0.out.value,  8)
#    self.assertEqual( model.out1.value,      8)
#    self.assertEqual( model.out2.value,      8)
#    self.assertEqual( model.out3.value,      8)
#    model.inp.value = 9
#    self.assertEqual( model.reg0.out.value,  8)
#    self.assertEqual( model.out1.value,      8)
#    self.assertEqual( model.out2.value,      8)
#    self.assertEqual( model.out3.value,      8)
#    model.inp.value = 10
#    sim.cycle()
#    self.assertEqual( model.reg0.out.value, 10)
#    self.assertEqual( model.out1.value,     10)
#    self.assertEqual( model.out2.value,     10)
#    self.assertEqual( model.out3.value,     10)
#    sim.cycle()
#    self.assertEqual( model.reg0.out.value, 10)
#    self.assertEqual( model.out1.value,     10)
#    self.assertEqual( model.out2.value,     10)
#    self.assertEqual( model.out3.value,     10)
#    sim.cycle()
#    self.assertEqual( model.reg0.out.value, 10)
#    self.assertEqual( model.out1.value,     10)
#    self.assertEqual( model.out2.value,     10)
#    self.assertEqual( model.out3.value,     10)
#
#  def test_fanout_two(self):
#    model = FanOutTwo(16)
#    sim = self.setup_sim(model)
#    sim.reset()
#    model.inp.value = 8
#    self.assertEqual( model.reg0.out.value,  0)
#    self.assertEqual( model.out1.value,      0)
#    self.assertEqual( model.out2.value,      0)
#    self.assertEqual( model.out3.value,      0)
#    sim.cycle()
#    self.assertEqual( model.reg0.out.value,  8)
#    self.assertEqual( model.out1.value,      0)
#    self.assertEqual( model.out2.value,      0)
#    self.assertEqual( model.out3.value,      0)
#    model.inp.value = 9
#    self.assertEqual( model.reg0.out.value,  8)
#    self.assertEqual( model.out1.value,      0)
#    self.assertEqual( model.out2.value,      0)
#    self.assertEqual( model.out3.value,      0)
#    model.inp.value = 10
#    sim.cycle()
#    self.assertEqual( model.reg0.out.value, 10)
#    self.assertEqual( model.out1.value,      8)
#    self.assertEqual( model.out2.value,      8)
#    self.assertEqual( model.out3.value,      8)
#    sim.cycle()
#    self.assertEqual( model.reg0.out.value, 10)
#    self.assertEqual( model.out1.value,     10)
#    self.assertEqual( model.out2.value,     10)
#    self.assertEqual( model.out3.value,     10)
#    sim.cycle()
#    self.assertEqual( model.reg0.out.value, 10)
#    self.assertEqual( model.out1.value,     10)
#    self.assertEqual( model.out2.value,     10)
#    self.assertEqual( model.out3.value,     10)
#
#class TestCombAndPosedge(unittest.TestCase):
#
#  def setup_sim(self, model):
#    model.elaborate()
#    sim = SimulationTool(model)
#    if debug_verbose:
#      debug_utils.port_walk(model)
#    return sim
#
#  def test_incrementer(self):
#    model = Incrementer()
#    sim = self.setup_sim(model)
#    sim.reset()
#    model.inp.value = 8
#    self.assertEqual( model.out.value, 1)
#    for i in xrange(10):
#      model.inp.value = i
#      sim.cycle()
#      self.assertEqual( model.out.value, i+1)
#
#  def test_counter(self):
#    model = Counter(7)
#    sim = self.setup_sim(model)
#    model.clear.value = 1
#    sim.reset()
#    model.clear.value = 0
#    self.assertEqual( model.count.value, 0)
#    expected = [1,2,3,4,5,6,7,0,1,2,
#                0,1,2,3,4,5,6,7,0,1]
#    for i in xrange(20):
#      if i == 10:
#        model.clear.value = 1
#      else:
#        model.clear.value = 0
#      sim.cycle()
#      self.assertEqual( model.count.value, expected[i])
#
#  def test_count_incr(self):
#    model = CountIncr(7)
#    sim = self.setup_sim(model)
#    model.clear.value = 1
#    sim.reset()
#    model.clear.value = 0
#    self.assertEqual( model.count.value, 1)
#    expected = [1,2,3,4,5,6,7,0,1,2,
#                0,1,2,3,4,5,6,7,0,1]
#    for i in xrange(20):
#      if i == 10:
#        model.clear.value = 1
#      else:
#        model.clear.value = 0
#      sim.cycle()
#      self.assertEqual( model.count.value, expected[i]+1)
#
#  def test_reg_incr(self):
#    model = RegIncr()
#    sim = self.setup_sim(model)
#    sim.reset()
#    model.inp.value = 8
#    self.assertEqual( model.out.value, 1)
#    for i in xrange(20):
#      model.inp.value = i
#      sim.cycle()
#      self.assertEqual( model.out.value, i+1)
#
#  def test_reg_incr_2(self):
#    # Build model and simulator
#    model = RegIncr()
#    sim = self.setup_sim(model)
#    # Define line_trace() add it to our model
#    def line_trace( self ):
#      return "in: {:4}  out: {:4}".format(self.inp.value, self.out.value)
#    # Dynamically bind line_trace to our object
#    import types
#    model.line_trace = types.MethodType( line_trace, model )
#    sim.en_line_trace()
#    sim.reset()
#    # Declare utility function
#    def cycle( in_, bw, out ):
#      model.inp.value = in_
#      sim.eval_combinational()
#      assert model.incr.inp.value == bw
#      assert model.out.value      == out
#      sim.cycle()
#    # Tests:  in   bw  out
#    cycle(     1,   0,   1 )
#    cycle(     2,   1,   2 )
#    cycle(    13,   2,   3 )
#    cycle(    42,  13,  14 )
#    cycle(    42,  42,  43 )
#    cycle(    42,  42,  43 )
#    cycle(    42,  42,  43 )
#    cycle(    51,  42,  43 )
#    cycle(    51,  51,  52 )
#
#  def test_incr_reg(self):
#    model = IncrReg()
#    sim = self.setup_sim(model)
#    sim.reset()
#    model.inp.value = 8
#    self.assertEqual( model.out.value, 1)
#    for i in xrange(20):
#      model.inp.value = i
#      sim.cycle()
#      self.assertEqual( model.out.value, i+1)
#
#  def test_incr_reg_2(self):
#    # Build model and simulator
#    model = IncrReg()
#    sim = self.setup_sim(model)
#    sim.reset()
#    # Declare utility function
#    def cycle( in_, bw, out ):
#      model.inp.value = in_
#      sim.eval_combinational()
#      assert model.reg0.inp.value == bw
#      assert model.out.value      == out
#      sim.cycle()
#    # Tests:  in   bw  out
#    cycle(     1,   2,   1 )
#    cycle(     2,   3,   2 )
#    cycle(    13,  14,   3 )
#    cycle(    42,  43,  14 )
#    cycle(    42,  43,  43 )
#    cycle(    42,  43,  43 )
#    cycle(    42,  43,  43 )
#    cycle(    51,  52,  43 )
#    cycle(    51,  52,  52 )
#
#  def test_gcd(self):
#    model = GCD()
#    sim = self.setup_sim(model)
#    sim.reset()
#    def util_test( a, b, out ):
#      #model.line_trace()
#      model.in_A.value   = a
#      model.in_B.value   = b
#      model.in_val.value = 1
#      sim.cycle()
#      #model.line_trace()
#      model.in_val.value = 0
#      done = False
#      for i in xrange(15):
#        #model.line_trace()
#        sim.cycle()
#        if model.out_val.value == True:
#          done = True
#          #model.line_trace()
#          self.assertEqual( model.out.value, out )
#          sim.cycle()
#          break
#      self.assertEqual( done, True )
#    util_test( 15, 5, 5 )
#    util_test( 5, 15, 5 )
#    util_test( 5, 8, 1 )
#    util_test( 12, 3, 3 )
#    util_test( 7, 4, 1 )
#    util_test( 7, 0, 7 )
#
#  def test_overflow(self):
#    model = Overflow()
#    sim = self.setup_sim(model)
#    sim.reset()
#    model.in0.value = 2
#    model.in1.value = 1
#    sim.cycle()
#    self.assertEqual( model.out.value, 1 )
#    model.out.value
#    model.in0.value = 2
#    model.in1.value = 0
#    sim.cycle()
#    self.assertEqual( model.out.value, 2 )
#    model.in0.value = 1
#    model.in1.value = 2
#    sim.cycle()
#    self.assertEqual( model.out.value, (2**16 - 1) )
#
#  def test_child_module_sensitivity1(self):
#    # Build model and simulator
#    model = ChildModuleSensitivity1()
#    sim = self.setup_sim(model)
#    sim.reset()
#    # Declare utility function
#    def cycle( in0, reg_out, incr_out, out ):
#      model.in0.value = in0
#      sim.eval_combinational()
#      assert model.reg0.out.value == reg_out
#      assert model.incr.out.value == incr_out
#      assert model.out.value      == out
#      sim.cycle()
#      assert model.reg0.inp.value == in0
#    # Tests:  in0  reg  inc  out
#    cycle(      2,   0,   1,   3 )
#    cycle(      4,   2,   3,   5 )
#    cycle(      2,   4,   5,   7 )
#    cycle(      2,   2,   3,   5 )
#    cycle(      2,   2,   3,   5 )
#    cycle(      2,   2,   3,   5 )
#
#  def test_child_module_sensitivity2(self):
#    # Build model and simulator
#    model = ChildModuleSensitivity2()
#    sim = self.setup_sim(model)
#    sim.reset()
#    # Declare utility function
#    def cycle( in0, in1, out ):
#      model.in0.value = in0
#      model.in1.value = in1
#      sim.eval_combinational()
#      assert model.out.value      == out
#      sim.cycle()
#      assert model.reg0.inp.value == in0
#      assert model.reg1.inp.value == in1
#    # Tests:  in0  in1  out
#    cycle(      2,   2,   0 )
#    cycle(      2,   4,   4 )
#    cycle(      2,   4,   6 )
#    cycle(      2,   4,   6 )
#    cycle(      2,   4,   6 )
#
#
if __name__ == '__main__':
  unittest.main()
