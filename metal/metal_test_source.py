#=========================================================================
# Test Source
#=========================================================================

from metal_model import *
from metal_simulate import LogicSim

class TestSource (Module):

  def __init__( self, n, msg_list ):
    self.out_msg = OutPort(n)
    self.out_val = OutPort(1)
    self.out_rdy = InPort(1)

    self.msg_list = msg_list
    self.idx = 0

  @posedge_clk
  def seq_logic( self ):

    out_msg = self.out_msg
    out_val = self.out_val
    out_rdy = self.out_rdy

    if ( (self.idx < len(self.msg_list)) ):
      out_msg.value = self.msg_list[self.idx]
      out_val.value = 1
      self.idx += 1
    else:
      out_val = 0

  def line_trace( self ):
    return "{0:3} {1:3} {2:4}".format( self.out_val.value,
                                       self.out_rdy.value,
                                       self.out_msg.value )

  def done( self ):
    return ( self.idx == len(self.msg_list) )


if __name__ == '__main__':

  msg_list = [ 1, 3, 5, 7, 9 ]

  model = TestSource(8,msg_list)
  model.elaborate()

  sim = LogicSim( model )
  sim.generate()

  cycle_count = 0
  model.out_rdy.value = 1
  print "{0:6} {1:3} {2:3} {3:4}".format('', 'val', 'rdy', 'data')
  print "{0:4} : {1}".format( cycle_count, model.line_trace())
  while ( not model.done() ):
    sim.cycle()
    cycle_count += 1
    print "{0:4} : {1}".format( cycle_count, model.line_trace())
