from rtler_translate import ToVerilog
from rtler_simulate  import LogicSim
from rtler_adder import *
import rtler_debug

#TODO: run pychecker?

########################################################################
# FullAdder
########################################################################

## Instantiate and Elaborate the FullAdder Module
#print "// Simulate FullAdder:"
#one_bit = FullAdder()
#one_bit.elaborate()

# Generate a simulator for the FullAdder
#sim = LogicSim( one_bit )
#sim.generate()
#
## Test the FullAdder Module
#import itertools
#for x,y,z in itertools.product([0,1], [0,1], [0,1]):
#  one_bit.in0.value = x
#  one_bit.in1.value = y
#  one_bit.cin.value = z
#  one_bit.logic()
#  #sim.cycle()  # TODO: DOESN'T WORK!
#  print "// Inputs:",
#  print one_bit.in0.value,
#  print one_bit.in1.value,
#  print one_bit.cin.value
#  print "// Outputs:",
#  print "sum:",  one_bit.sum.value,
#  print "cout:", one_bit.cout.value

## Generate Verilog for the FullAdder Module
#v = ToVerilog( one_bit )
#v.generate( sys.stdout )

########################################################################
# RippleCarryAdder
########################################################################

## Instantiate and Elaborate the RippleCarryAdder Module
#print "// Simulate RippleCarryAdder:"
#four_bit = RippleCarryAdder(4)
#four_bit.elaborate()
#
## Generate a simulator for the Ripple Carry Adder
#sim = LogicSim( four_bit )
#sim.generate()
#
## Test the RippleCarryAdder Module
#rtler_debug.port_walk(four_bit)
#four_bit.in0.value = 11
#four_bit.in1.value = 4
#sim.cycle()
#print "// Result:", four_bit.sum.value
#
## Generate Verilog for the RippleCarryAdder Module
#v = ToVerilog( four_bit )
#v.generate( sys.stdout )

########################################################################
# ManyAdders
########################################################################

# Instantiate and Elaborate ManyAdders
NUM_BITS   = 8
NUM_ADDERS = 3
print "// Simulate ManyAdders:"
many = ManyAdders(NUM_BITS, NUM_ADDERS)
many.elaborate()

# Generate a simulator for ManyAdders
sim = LogicSim( many )
sim.generate()
#sim.dump_graphviz()

# Test ManyAdders
#rtler_debug.port_walk(four_bit)
many.in0 = 5
for i in range(NUM_ADDERS):
  # TODO: a way to check for slice access vs. array? Could be confusing
  many.in1[i].value = (i+1)*2
sim.cycle()
for i in range(NUM_ADDERS):
  print "// Result:", many.sum[i].value

# Generate Verilog for ManyAdders
v = ToVerilog( many )
v.generate( sys.stdout )


########################################################################
# AdderChain: Debugging
########################################################################

## Instantiate and Elaborate the AdderChain Module
#print "// Simulate AdderChain:"
#two_test = AdderChain( 5 )
#two_test.elaborate()
##rtler_debug.port_walk(two_test)
#
## Generate a simulator for the AdderChain
#sim = LogicSim( two_test )
#sim.generate()
#
## Test the AdderChain Module
#two_test.in0.value = 1
#two_test.in1.value = 0
#sim.cycle()
#print "// Result:", two_test.sum.value
#
## Generate Verilog for the AdderChain Module
#v = ToVerilog( two_test )
#v.generate( sys.stdout )

