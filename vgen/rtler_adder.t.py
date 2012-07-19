from rtler_translate import ToVerilog
from rtler_adder import *
import rtler_debug

#TODO: run pychecker?
# Instantiate ToVerilog translator
v = ToVerilog()


########################################################################
# FullAdder
########################################################################

# Instantiate and Elaborate the FullAdder Module
print "// Simulate FullAdder:"
one_bit = FullAdder()
one_bit.elaborate()

# Test the FullAdder Module
import itertools
for x,y,z in itertools.product([0,1], [0,1], [0,1]):
  one_bit.in0.value = x
  one_bit.in1.value = y
  one_bit.cin.value = z
  one_bit.logic()
  #sim.cycle()  # TODO: DOESN'T WORK!
  print "// Inputs:",
  print one_bit.in0.value,
  print one_bit.in1.value,
  print one_bit.cin.value
  print "// Outputs:",
  print "sum:",  one_bit.sum.value,
  print "cout:", one_bit.cout.value

# Generate Verilog for the FullAdder Module
v.generate( one_bit, sys.stdout )

########################################################################
# RippleCarryAdder
########################################################################

# Instantiate and Elaborate the RippleCarryAdder Module
print "// Simulate RippleCarryAdder:"
four_bit = RippleCarryAdder(4)
four_bit.elaborate()
sim.generate( four_bit )

# Test the RippleCarryAdder Module
#rtler_debug.port_walk(four_bit)
four_bit.in0.value = 11
four_bit.in1.value = 4
sim.cycle()
print "// Result:", four_bit.sum.value

# Generate Verilog for the RippleCarryAdder Module
v.generate( four_bit, sys.stdout )


########################################################################
# AdderChain: Debugging
########################################################################

## Instantiate and Elaborate the AdderChain Module
#print "// Simulate AdderChain:"
#two_test = AdderChain( 5 )
#two_test.elaborate()
#
## Test the AdderChain Module
##rtler_debug.port_walk(two_test)
#sim.generate( two_test )
#two_test.in0.value = 1
#two_test.in1.value = 0
#sim.cycle()
#print "// Result:", two_test.sum.value
#
## Generate Verilog for the AdderChain Module
#v.generate( two_test, sys.stdout )

