#=========================================================================
# RingRouter
#=========================================================================

from pymtl import *
import pmlib

from math import ceil, log

# TODO: better way to set this parameter?
BUFFERING = 3

#=========================================================================
# Ring Router
#=========================================================================

class RingRouter ( Model ):

  def __init__( self, id, num_nodes, payload_nbits ):

    self.id     = id
    self.nodes  = num_nodes
    srcdest_nbits = int( ceil( log( num_nodes, 2 ) ) )
    self.msg = pmlib.net_msgs.NetMsgParams( srcdest_nbits, payload_nbits )

    #---------------------------------------------------------------------
    # Line tracing
    #---------------------------------------------------------------------

    msg_sz = self.msg.nbits

    self.in_msg     = [ InPort  ( msg_sz ) for x in range(3) ]
    self.in_val     = [ InPort  ( 1 )      for x in range(3) ]
    self.in_credit  = [ OutPort ( 1 )      for x in range(3) ]

    self.out_msg    = [ OutPort ( msg_sz ) for x in range(3) ]
    self.out_val    = [ OutPort ( 1 )      for x in range(3) ]
    self.out_credit = [ InPort  ( 1 )      for x in range(3) ]

    #---------------------------------------------------------------------
    # Static Elaboration
    #---------------------------------------------------------------------

    self.dpath = RingRouterDpath ( id, num_nodes, payload_nbits ):
    self.ctrl  = RingRouterCtrl  ( id, num_nodes, payload_nbits ):

    dest = self.msg.dest_slice

    for i in range(3):

      connect( self.dpath.in_enq_msg[i],     self.in_msg[i]           )
      connect( self.dpath.in_enq_val[i],     self.in_val[i]           )
      connect( self.dpath.out_deq_msg[i],    self.out_msg[i]          )
      connect( self.dpath.out_deq_val[i],    self.out_val[i]          )

      connect( self.ctrl.in_deq_msg_dest[i], self.in_msg[i][dest]     )
      connect( self.ctrl.in_credit[i],       self.in_val[i]           )
      connect( self.ctrl.out_credit[i],      self.out_msg[i]          )

      connect( self.dpath.in_deq_val[i],     self.ctrl.in_deq_val[i]  )
      connect( self.dpath.in_deq_rdy[i],     self.ctrl.in_deq_rdy[i]  )
      connect( self.dpath.out_enq_val[i],    self.ctrl.out_enq_val[i] )
      connect( self.dpath.xbar_sel[i],       self.ctrl.xbar_sel[i]    )

  #-----------------------------------------------------------------------
  # Line tracing
  #-----------------------------------------------------------------------

  #def line_trace( self ):

  #  in_str = \
  #    pmlib.valrdy.valrdy_to_str( self.enq_bits.value,
  #      self.enq_val.value, self.enq_rdy.value )

  #  out_str = \
  #    pmlib.valrdy.valrdy_to_str( self.deq_bits.value,
  #      self.deq_val.value, self.deq_rdy.value )

  #  return "{} () {}"\
  #    .format( in_str, out_str )


#=========================================================================
# Ring Router Datapath
#=========================================================================

class RingRouterDpath (Model):

  def __init__( self, id, num_nodes, payload_nbits ):

    self.id     = id
    self.nodes  = num_nodes
    srcdest_nbits = int( ceil( log( num_nodes, 2 ) ) )
    self.msg = pmlib.net_msgs.NetMsgParams( srcdest_nbits, payload_nbits )

    #---------------------------------------------------------------------
    # Interface Ports
    #---------------------------------------------------------------------

    msg_sz = self.msg.nbits

    self.in_enq_msg      = [ InPort  ( msg_sz ) for x in range(3) ]
    self.in_enq_val      = [ InPort  ( 1 )      for x in range(3) ]

    self.out_deq_msg     = [ OutPort ( msg_sz ) for x in range(3) ]
    self.out_deq_val     = [ OutPort ( 1 )      for x in range(3) ]

    self.in_deq_val      = [ OutPort ( 1 )      for x in range(3) ]
    self.in_deq_rdy      = [ InPort  ( 1 )      for x in range(3) ]
    self.out_enq_val     = [ InPort  ( 1 )      for x in range(3) ]
    self.xbar_sel        = [ InPort  ( 2 )      for x in range(3) ]

    #---------------------------------------------------------------------
    # Static Elaboration
    #---------------------------------------------------------------------

    self.in_queues  = [ NormalQueue( BUFFERING, msg_sz ) for x in range(3) ]
    self.out_queues = [ NormalQueue( BUFFERING, msg_sz ) for x in range(3) ]
    self.xbar       = Crossbar( 3, msg_sz )

    for i in range(3):

      # Input Queues (enq_rdy left floating)

      connect( self.in_queues[i].enq_bits,  self.in_enq_msg[i]  )
      connect( self.in_queues[i].enq_val,   self.in_enq_val[i]  )

      connect( self.in_queues[i].deq_bits,  self.xbar.in_[i]    )
      connect( self.in_queues[i].deq_val,   self.in_deq_val[i]  )
      connect( self.in_queues[i].deq_rdy,   self.in_deq_rdy[i]  )

      # Output Queues (enq_rdy left floating)

      connect( self.out_queues[i].enq_bits, self.xbar.out[i]    )
      connect( self.out_queues[i].enq_val,  self.out_enq_val[i] )

      connect( self.out_queues[i].deq_bits, self.out_deq_msg[i] )
      connect( self.out_queues[i].deq_val,  self.out_deq_val[i] )
      connect( self.out_queues[i].deq_rdy,  1                   )

      # Crossbar

      connect( self.xbar.sel[i],            self.xbar_sel[i]    )


#=========================================================================
# Ring Router Control
#=========================================================================

class RingRouterCtrl (Model):

  def __init__( self, id, num_nodes, payload_nbits ):

    self.id     = id
    self.nodes  = num_nodes
    srcdest_nbits = int( ceil( log( num_nodes, 2 ) ) )
    self.msg = pmlib.net_msgs.NetMsgParams( srcdest_nbits, payload_nbits )

    #---------------------------------------------------------------------
    # Interface Ports
    #---------------------------------------------------------------------

    msg_sz = self.msg.srcdest_nbits

    self.in_deq_msg_dest = [ InPort  ( msg_sz ) for x in range(3) ]
    self.in_credit       = [ OutPort ( 1 )      for x in range(3) ]

    self.out_credit      = [ InPort  ( 1 )      for x in range(3) ]

    self.in_deq_val      = [ InPort  ( 1 )      for x in range(3) ]
    self.in_deq_rdy      = [ OutPort ( 1 )      for x in range(3) ]
    self.out_enq_val     = [ OutPort ( 1 )      for x in range(3) ]
    self.xbar_sel        = [ OutPort ( 2 )      for x in range(3) ]

    #---------------------------------------------------------------------
    # Static Elaboration
    #---------------------------------------------------------------------

    self.ictrl = [ InputCtrl  ( ? ) for x in range(3) ]
    self.octrl = [ OutputCtrl ( ? ) for x in range(3) ]

    for i in range(3):

      connect( self.ictrl[i].in_deq_msg_dest, self.in_deq_msg_dest[i] )
      connect( self.ictrl[i].in_deq_val,      self.in_deq_val[i]      )
      connect( self.ictrl[i].in_deq_rdy,      self.in_deq_rdy[i]      )
      connect( self.ictrl[i].in_credit,       self.in_credit[i]       )

      connect( self.octrl[i].out_enq_val,     self.out_enq_val[i]     )
      connect( self.octrl[i].out_credit,      self.out_credit[i]      )

   # TODO: bubble flow control, credit_count signal!
   # connect( self.ictrl[1].credit_count[0], self.octrl[0].credit_count )
   # connect( self.ictrl[1].credit_count[1], self.octrl[2].credit_count )

   @combinational
   def assign_reqs_grants( self ):

     for i in range(3):
       for j in range(3):
         self.octrl[i].reqs.value[j]   = self.ictrl[j].reqs.value[i]
         self.ictrl[i].grants.value[j] = self.octrl[j].grants.value[i]


#=========================================================================
# Input Terminal Control
#=========================================================================

class InputCtrl(Model):

  def __init__( self, size, nbits ):

    #---------------------------------------------------------------------
    # Interface Ports
    #---------------------------------------------------------------------

    self.in_deq_msg_dest = InPort  ( ??? )
    self.in_deq_val      = InPort  ( 1 )
    self.in_deq_rdy      = OutPort ( 1 )
    self.in_credit       = OutPort ( 1 )

    self.reqs            = OutPort ( 3 )
    self.grants          = InPort  ( 3 )

    self.WEST = 0
    self.THIS = 1
    self.EAST = 2

  #-----------------------------------------------------------------------
  # Route Computation
  #-----------------------------------------------------------------------

  def route( self, dest, id, nodes ):

    if ( dest < id ):
      dist_east = dest + ( nodes - id )
      dist_west = id - dest
    else:
      dist_east = dest - id
      dist_west = id + ( nodes - dest )

    if ( dest == id ):
      return THIS
    elif ( dist_east < dist_west ):
      return EAST
    else:
      return WEST

  #-----------------------------------------------------------------------
  # Combinational Logic
  #-----------------------------------------------------------------------

  @combinational
  def comb_logic( self ):

    dest = route( self.in_deq_msg_dest.value, self.id, self.nodes )

    self.reqs.value[0] = self.in_deq_val.value and ( dest == self.WEST )
    self.reqs.value[1] = self.in_deq_val.value and ( dest == self.THIS )
    self.reqs.value[2] = self.in_deq_val.value and ( dest == self.EAST )

    self.in_deq_rdy.value = ( ( self.grants.value[0] & self.reqs.value[0] )
                            | ( self.grants.value[1] & self.reqs.value[1] )
                            | ( self.grants.value[2] & self.reqs.value[2] ))

  #-----------------------------------------------------------------------
  # Sequential Logic
  #-----------------------------------------------------------------------

  @posedge_clk
  def seq_logic( self ):

    self.in_credit.next = self.in_deq_rdy.value


#=========================================================================
# Output Terminal Control
#=========================================================================

class OutputCtrl(Model):

  def __init__( self, size, nbits ):

    #---------------------------------------------------------------------
    # Interface Ports
    #---------------------------------------------------------------------

    self.out_enq_val     = OutPort ( 1 )
    self.out_credit      = InPort  ( 1 )
    self.xbar_sel        = InPort  ( 2 )

    self.reqs            = InPort  ( 3 )
    self.grants          = OutPort ( 3 )

    #---------------------------------------------------------------------
    # Submodules
    #---------------------------------------------------------------------

    self.arb             = RoundRobinArbiter( 3 )

  #-----------------------------------------------------------------------
  # Credit Counter
  #-----------------------------------------------------------------------

  @posedge_clk
  def counter( self ):

    if self.reset.value:
      self.counter.value = BUFFERING
    elif self.out_credit.value and not self.out_enq_val.value:
      self.counter.value = self.counter.value + 1
    elif self.out_enq_val.value and not self.out_credit.value:
      self.counter.value = self.counter.value - 1
    else:
      self.counter.value = self.counter.value

  #-----------------------------------------------------------------------
  # Arbitation/Crossbar Signals
  #-----------------------------------------------------------------------

  @combinational
  def logic( self ):

    # Set arbiter request signals

    if self.counter.value == 0:
      self.arb.reqs.value = 0
      self.grants.value   = 0
    else:
      self.arb.reqs.value = self.reqs.value
      self.grants.value   = self.arb.grants.value

    # Set valid signal

    self.out_enq_val.value = ( ( self.grants.value[0] & self.reqs.value[0] )
                             | ( self.grants.value[1] & self.reqs.value[1] )
                             | ( self.grants.value[2] & self.reqs.value[2] ))

    # Set crossbar select

    if   self.grants.value[0]:
      self.xbar_sel.value = 0
    elif self.grants.value[1]:
      self.xbar_sel.value = 1
    else:
      self.xbar_sel.value = 2

