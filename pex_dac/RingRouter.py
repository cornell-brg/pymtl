#=========================================================================
# RingRouter
#=========================================================================

from pymtl import *
import pmlib

from pmlib.NormalQueue import NormalQueue
from pmlib.arbiters    import RoundRobinArbiterEn

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
    self.msg = pmlib.net_msgs.NetMsgParams( num_nodes, 2, payload_nbits )

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

    self.dpath = RingRouterDpath ( id, num_nodes, payload_nbits )
    self.ctrl  = RingRouterCtrl  ( id, num_nodes, payload_nbits )

    dest = self.msg.dest_slice

    for i in range(3):

      connect( self.dpath.in_enq_msg[i],     self.in_msg[i]           )
      connect( self.dpath.in_enq_val[i],     self.in_val[i]           )
      connect( self.dpath.out_deq_msg[i],    self.out_msg[i]          )
      connect( self.dpath.out_deq_val[i],    self.out_val[i]          )

      connect( self.ctrl.in_deq_msg_dest[i], self.in_msg[i][dest]     )
      connect( self.ctrl.in_credit[i],       self.in_val[i]           )
      connect( self.ctrl.out_credit[i],      self.out_credit[i]       )

      connect( self.dpath.in_deq_val[i],     self.ctrl.in_deq_val[i]  )
      connect( self.dpath.in_deq_rdy[i],     self.ctrl.in_deq_rdy[i]  )
      connect( self.dpath.out_enq_val[i],    self.ctrl.out_enq_val[i] )
      connect( self.dpath.xbar_sel[i],       self.ctrl.xbar_sel[i]    )

  #-----------------------------------------------------------------------
  # Line tracing
  #-----------------------------------------------------------------------

  def line_trace( self ):

    traces = []
    for i in range( 3 ):
      in_str = \
        pmlib.valrdy.valrdy_to_str( self.in_msg[i].value,
          self.in_val[i].value, 1 )

      in_credit = '+' if self.in_credit[i].value else ' '

      out_str = \
        pmlib.valrdy.valrdy_to_str( self.out_msg[i].value,
          self.out_val[i].value, 1 )

      out_credit = '+' if self.out_credit[i].value else ' '

      traces += ["{} {} () {} {}"\
        .format( in_str, in_credit, out_str, out_credit )]


    return ' | '.join( traces )


#=========================================================================
# Ring Router Datapath
#=========================================================================

class RingRouterDpath (Model):

  def __init__( self, id, num_nodes, payload_nbits ):

    self.id     = id
    self.nodes  = num_nodes
    self.msg = pmlib.net_msgs.NetMsgParams( num_nodes, 2, payload_nbits )

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
    self.xbar       = pmlib.Crossbar( 3, msg_sz )

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
    self.msg = pmlib.net_msgs.NetMsgParams( num_nodes, 2, payload_nbits )

    #---------------------------------------------------------------------
    # Interface Ports
    #---------------------------------------------------------------------

    dest_sz = self.msg.srcdest_nbits

    self.in_deq_msg_dest = [ InPort  ( dest_sz ) for x in range(3) ]
    self.in_credit       = [ OutPort ( 1 )       for x in range(3) ]

    self.out_credit      = [ InPort  ( 1 )       for x in range(3) ]

    self.in_deq_val      = [ InPort  ( 1 )       for x in range(3) ]
    self.in_deq_rdy      = [ OutPort ( 1 )       for x in range(3) ]
    self.out_enq_val     = [ OutPort ( 1 )       for x in range(3) ]
    self.xbar_sel        = [ OutPort ( 2 )       for x in range(3) ]

    #---------------------------------------------------------------------
    # Static Elaboration
    #---------------------------------------------------------------------

    self.ictrl = [ InputCtrl  ( id, num_nodes, dest_sz ) for x in range(3) ]
    self.octrl = [ OutputCtrl ( )                        for x in range(3) ]

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
        self.octrl[i].reqs[j].value   = self.ictrl[j].reqs[i].value
        self.ictrl[i].grants[j].value = self.octrl[j].grants[i].value


#=========================================================================
# Input Terminal Control
#=========================================================================

class InputCtrl(Model):

  def __init__( self, id, num_nodes, dest_sz ):

    self.id    = id
    self.nodes = num_nodes

    #---------------------------------------------------------------------
    # Interface Ports
    #---------------------------------------------------------------------

    self.in_deq_msg_dest = InPort  ( dest_sz )
    self.in_deq_val      = InPort  ( 1 )
    self.in_deq_rdy      = OutPort ( 1 )
    self.in_credit       = OutPort ( 1 )

    self.reqs            = OutPort ( 3 )
    self.grants          = InPort  ( 3 )

    self.dest            = Wire    ( 2 )

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
      return self.THIS
    elif ( dist_east < dist_west ):
      return self.EAST
    else:
      return self.WEST

  #-----------------------------------------------------------------------
  # Combinational Logic
  #-----------------------------------------------------------------------

  @combinational
  def comb_logic( self ):

    self.dest.value = self.route( self.in_deq_msg_dest.value.uint, self.id, self.nodes )

    # TODO: self.reqs.value[x] is what we want, but this fails
    #       to update the VCD correctly!
    self.reqs[0].value = self.in_deq_val.value and ( self.dest.value == self.WEST )
    self.reqs[1].value = self.in_deq_val.value and ( self.dest.value == self.THIS )
    self.reqs[2].value = self.in_deq_val.value and ( self.dest.value == self.EAST )

    self.in_deq_rdy.value = ( ( self.grants[0].value & self.reqs[0].value )
                            | ( self.grants[1].value & self.reqs[1].value )
                            | ( self.grants[2].value & self.reqs[2].value ))

    #print "DEQRDY", self.name, "r", self.reqs.value.uint, "g", self.grants.value.uint, self.in_deq_rdy.value.uint

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

  def __init__( self ):

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

    max_credits_nbits    = int( ceil( log( BUFFERING+1, 2 ) ) )

    self.credits         = Wire( max_credits_nbits )
    self.arb_en          = Wire( 1 )

    self.arb             = RoundRobinArbiterEn( 3 )

    connect( self.reqs,   self.arb.reqs   )
    connect( self.grants, self.arb.grants )
    connect( self.arb_en, self.arb.en     )

  #-----------------------------------------------------------------------
  # Credit Counter
  #-----------------------------------------------------------------------

  @posedge_clk
  def credit_logic( self ):

    if self.reset.value:
      self.credits.next = BUFFERING
    elif self.out_credit.value and not self.out_enq_val.value:
      assert self.credits.value < BUFFERING
      self.credits.next = self.credits.value + 1
    elif self.out_enq_val.value and not self.out_credit.value:
      assert self.credits.value > 0
      self.credits.next = self.credits.value - 1
    else:
      self.credits.next = self.credits.value

  #-----------------------------------------------------------------------
  # Arbitation/Crossbar Signals
  #-----------------------------------------------------------------------

  @combinational
  def logic( self ):

    # Set arbiter request signals
    self.arb_en.value = ( self.credits.value != 0 )

    #if self.credits.value == 0:
    #  self.arb.reqs.value = 0
    #  self.grants.value   = 0
    #else:
    #  self.arb.reqs.value = self.reqs.value
    #  self.grants.value   = self.arb.grants.value

    # Set valid signal

    self.out_enq_val.value = ( ( self.grants[0].value & self.reqs[0].value )
                             | ( self.grants[1].value & self.reqs[1].value )
                             | ( self.grants[2].value & self.reqs[2].value ))

    #print "ENQRDY", self.name, "r", self.reqs.value.uint, "g", self.grants.value.uint, self.out_enq_val.value.uint

    # Set crossbar select

    if   self.grants[0].value:
      self.xbar_sel.value = 0
    elif self.grants[1].value:
      self.xbar_sel.value = 1
    else:
      self.xbar_sel.value = 2

