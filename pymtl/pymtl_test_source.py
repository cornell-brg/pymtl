#=========================================================================
# Test Source
#=========================================================================

from pymtl_model import *
from pymtl_simulate import LogicSim

class TestSource (Model):

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

    if out_val.value and out_rdy.value:
      self.idx += 1

    if self.idx < len(self.msg_list):
      out_msg.next = self.msg_list[self.idx]
      out_val.next = 1
    else:
      out_val.next = 0

  def line_trace( self ):
    return "{0:3} {1:3} {2:4}".format( self.out_val.value,
                                       self.out_rdy.value,
                                       self.out_msg.value )

  def done( self ):
    return ( self.idx == len(self.msg_list) )


class TestSink(Model):

  def __init__( self, n, msg_list ):
    self.in_msg = InPort(n)
    self.in_val = InPort(1)
    self.in_rdy = OutPort(1)

    self.msg_list = msg_list
    self.idx = 0

  @posedge_clk
  def seq_logic( self ):

    in_msg = self.in_msg
    in_val = self.in_val
    in_rdy = self.in_rdy

    if in_val.value and in_rdy.value:
      assert in_msg.value == self.msg_list[self.idx]
      self.idx += 1

    if self.idx < len(self.msg_list):
      in_rdy.next = 1
    else:
      in_rdy.next = 0


  def line_trace( self ):
    return "{0:3} {1:3} {2:4}".format( self.in_val.value,
                                       self.in_rdy.value,
                                       self.in_msg.value )

  def done( self ):
    return ( self.idx == len(self.msg_list) )


class TestHarness(Model):
  def __init__( self, n, msg_list ):
    self.src  = TestSource(n, msg_list)
    self.sink = TestSink(n, msg_list)
    self.src.out_msg <> self.sink.in_msg
    self.src.out_val <> self.sink.in_val
    self.src.out_rdy <> self.sink.in_rdy

  def done( self ):
    return self.src.done() and self.sink.done()


if __name__ == '__main__':

  msg_list = [ 1, 3, 5, 7, 9 ]

  print
  print "Testing TestSource"
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


  print
  print "Testing TestSink"
  model = TestSink(8,msg_list)
  model.elaborate()

  sim = LogicSim( model )
  sim.generate()

  cycle_count = 0
  model.in_val.value = 1
  print "{0:6} {1:3} {2:3} {3:4}".format('', 'val', 'rdy', 'data')
  print "{0:4} : {1}".format( cycle_count, model.line_trace())
  i = 0
  while ( not model.done() ):
    model.in_msg.value = msg_list[i]
    if model.in_rdy.value:
      i += 1
    sim.cycle()
    cycle_count += 1
    print "{0:4} : {1}".format( cycle_count, model.line_trace())


  print
  print "Testing TestSource+TestSink"
  model = TestHarness(8,msg_list)
  model.elaborate()

  sim = LogicSim( model )
  sim.generate()
  cycle_count = 0
  print "{0:6} {1:3} {2:3} {3:4} | {4:3} {5:3} {6:4}".format(
          '', 'val', 'rdy', 'data', 'val', 'rdy','data')
  print "{0:4} : {1} | {2}".format( cycle_count, model.src.line_trace(),
                                                 model.sink.line_trace() )
  while ( not model.done() ):
    sim.cycle()
    cycle_count += 1
    print "{0:4} : {1} | {2}".format( cycle_count, model.src.line_trace(),
                                                   model.sink.line_trace() )
