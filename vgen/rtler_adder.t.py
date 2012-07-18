from rtler_translate import ToVerilog
from rtler_adder import *

v = ToVerilog()

def port_walk(tgt, spaces=0):
  for x in tgt.ports:
    print spaces*' ', x.parent, x
    for y in x.connection:
      print spaces*' ', '   knctn:', type(y), y.parent, y.name
    print spaces*' ', '   value:', x._value, x.value
  print
  for x in tgt.submodules:
    print spaces*' ', x.name
    port_walk(x, spaces+3)

#print "// Simulate FullAdder:"
#TODO: run pychecker?
one_bit = FullAdder()
import itertools
v.elaborate( one_bit )
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
v.generate( one_bit, sys.stdout )

#print "// Simulate AdderChain:"
#two_test = AdderChain( 1 )
#v.elaborate( two_test )
#port_walk(two_test)
#two_test.in0.value = 1
#two_test.in1.value = 1
#sim.cycle()
#print "// Result:", two_test.sum.value
#v.generate( two_test, sys.stdout )

print "// Simulate RippleCarryAdder:"
four_bit = RippleCarryAdder(4)
v.elaborate( four_bit )
#port_walk(four_bit)
four_bit.in0.value = 9
four_bit.in1.value = 1
sim.cycle()
print "// Result:", four_bit.sum.value
v.generate( four_bit, sys.stdout )
