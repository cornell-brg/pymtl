
import sys
from tutorial_gcd import GCD
from pymtl.pymtl_test_source import TestSource, TestSink
from pymtl.pymtl_model import *
from pymtl.pymtl_simulate import *
from pymtl.pymtl_visualize import *
from pymtl.pymtl_translate import *

######################################################################
# TEST HARNESS
######################################################################
class TestHarness(Model):

  def __init__( self, msg_list_1, msg_list_2, msg_list_3 ):
    self.src1 = TestSource(16, msg_list_1 )
    self.src2 = TestSource(16, msg_list_2 )
    self.sink = TestSink(16, msg_list_3 )
    self.gcd  = GCD()

    self.src1.out_msg <> self.gcd.in_A
    self.src2.out_msg <> self.gcd.in_B
    # TODO: really should be anding src1 and src2 val...
    #       will need to change this if we have random delay
    self.src1.out_val <> self.gcd.in_val
    self.src1.out_rdy <> self.gcd.in_rdy
    self.src2.out_rdy <> self.gcd.in_rdy

    self.gcd.out     <> self.sink.in_msg
    self.gcd.out_val <> self.sink.in_val
    self.gcd.out_rdy <> self.sink.in_rdy

  def done( self ):
    return self.src1.done() and self.src2.done() and self.sink.done()

######################################################################
# MAIN
######################################################################
if __name__ == '__main__':

  if len(sys.argv) < 2:
    print "Please choose a mode: [simulate, visualize, translate]"
    sys.exit()

  ######################################################################
  # Simulate
  ######################################################################
  msg_list_1 = [ 15,  5, 5, 12, 9, 7, 7 ]
  msg_list_2 = [  5, 15, 8,  3, 9, 4, 0 ]
  msg_list_3 = [  5,  5, 1,  3, 9, 1, 7 ]
  if sys.argv[1] == 'simulate':
    print "SIMULATING"
    print
    model = TestHarness( msg_list_1, msg_list_2, msg_list_3 )
    model.elaborate()

    sim = LogicSim( model )
    sim.generate()
    cycle_count = 0
    print "{0:6} {1:3} {2:3} {3:4} | {4:3} {5:3} {6:4}".format(
            '', 'val', 'rdy', 'data', 'val', 'rdy','data')
    print "{0:4} : {1} | {2} | {3}".format( cycle_count, model.src1.line_trace(),
                                                         model.src2.line_trace(),
                                                         model.sink.line_trace()),
    if model.sink.in_val.value and model.sink.in_rdy.value:
      print "YES"
    else:
      print

    while ( not model.done() ):
      sim.cycle()
      cycle_count += 1
      print "{0:4} : {1} | {2} | {3}".format( cycle_count, model.src1.line_trace(),
                                                           model.src2.line_trace(),
                                                           model.sink.line_trace() ),
      if model.sink.in_val.value and model.sink.in_rdy.value:
        print "YES"
      else:
        print

  ######################################################################
  # Visualize
  ######################################################################
  elif sys.argv[1] == 'visualize':
    print "VISUALIZING"
    model = TestHarness( msg_list_1, msg_list_2, msg_list_3 )
    model.elaborate()
    viz = GraphvizDiagram( model )
    viz.generate()
    viz.to_diagram('gcd.png')
    #viz.to_text()

  ######################################################################
  # Translate
  ######################################################################
  elif sys.argv[1] == 'translate':
    print "TRANSLATING"
    model = GCD()
    model.elaborate()
    tran = ToVerilog (model)
    fd = open('gcd.v', 'w')
    tran.generate(fd)

