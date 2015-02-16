#=======================================================================
# MeshRouterRTL.py
#=======================================================================

from math import sqrt

from pymtl        import *
from pclib.ifcs import InValRdyBundle, OutValRdyBundle, NetMsg
from pclib.rtl    import Crossbar, RoundRobinArbiterEn, NormalQueue

#=======================================================================
# MeshRouterRTL
#=======================================================================
class MeshRouterRTL( Model ):

  NORTH = 0
  EAST  = 1
  SOUTH = 2
  WEST  = 3
  TERM  = 4

  #---------------------------------------------------------------------
  # __init__
  #---------------------------------------------------------------------
  def __init__( s, id_, nrouters, nmessages, payload_nbits, nentries ):

    s.id_           = id_
    s.nrouters      = nrouters
    s.nmessages     = nmessages
    s.payload_nbits = payload_nbits
    s.nentries      = nentries

    s.msg_type      = NetMsg( nrouters, nmessages, payload_nbits )

    #-------------------------------------------------------------------
    # Interface
    #-------------------------------------------------------------------

    s.in_ = InValRdyBundle [ 5 ]( s.msg_type )
    s.out = OutValRdyBundle[ 5 ]( s.msg_type )

  #---------------------------------------------------------------------
  # elaborate_logic
  #---------------------------------------------------------------------
  def elaborate_logic( s ):

    s.dpath = MeshRouterRTLDpath( s.id_, s.nrouters, s.nmessages,
                                  s.payload_nbits, s.nentries )
    s.ctrl  = MeshRouterRTLCtrl ( s.id_, s.nrouters, s.nmessages,
                                  s.payload_nbits, s.nentries )

    for i in xrange( 5 ):
      s.connect( s.in_[i],      s.dpath.in_[i] )
      s.connect( s.out[i],      s.dpath.out[i] )
      s.connect( s.ctrl.c2d[i], s.dpath.c2d[i] )

  #---------------------------------------------------------------------
  # line_trace
  #---------------------------------------------------------------------
  def line_trace( s ):

    router_traces = []
    for i in range( 5 ):
      in_str  = s.in_[ i ].to_str( s.in_[ i ].msg.payload )
      out_str = s.out[ i ].to_str( s.out[ i ].msg.payload )
      router_traces += ['{} {}'.format( in_str, out_str ) ]

    return '|'.join( router_traces )

#-----------------------------------------------------------------------
# MeshRouterRTLDpath
#-----------------------------------------------------------------------
class MeshRouterRTLDpath( Model ):

  #---------------------------------------------------------------------
  # __init__
  #---------------------------------------------------------------------
  def __init__( s, id_, nrouters, nmessages, payload_nbits, nentries ):

    s.id_           = id_
    s.nrouters      = nrouters
    s.nmessages     = nmessages
    s.payload_nbits = payload_nbits
    s.nentries      = nentries

    s.msg_type      = NetMsg( nrouters, nmessages, payload_nbits )

    #-------------------------------------------------------------------
    # Interface
    #-------------------------------------------------------------------

    s.in_ = InValRdyBundle [ 5 ]( s.msg_type )
    s.out = OutValRdyBundle[ 5 ]( s.msg_type )
    s.c2d = [ DpathBundle( s.msg_type ) for x in xrange(5) ]

  #---------------------------------------------------------------------
  # elaborate_logic
  #---------------------------------------------------------------------
  def elaborate_logic( s ):

    # Input Queues
    s.q_in  = [ NormalQueue( s.nentries, s.msg_type ) for x in range( 5 ) ]

    # Crossbar
    s.xbar  = Crossbar( 5, s.msg_type )

    # Output Queues
    s.q_out = [ NormalQueue( s.nentries, s.msg_type ) for x in range( 5 ) ]

    for i in xrange( 5 ):
      s.connect( s.q_in [i].enq,      s.in_[i]            )

      s.connect( s.q_in [i].deq.msg,  s.c2d[i].inbuf_msg  )
      s.connect( s.q_in [i].deq.val,  s.c2d[i].inbuf_val  )
      s.connect( s.q_in [i].deq.rdy,  s.c2d[i].inbuf_rdy  )

      s.connect( s.q_in [i].deq.msg,  s.xbar.in_[i]       )
      s.connect( s.q_out[i].enq.msg,  s.xbar.out[i]       )
      s.connect( s.c2d  [i].xbar_sel, s.xbar.sel[i]       )

      s.connect( s.q_out[i].enq.val,  s.c2d[i].outbuf_val )
      s.connect( s.q_out[i].enq.rdy,  s.c2d[i].outbuf_rdy )

      s.connect( s.q_out[i].deq,      s.out[i]            )

#-----------------------------------------------------------------------
# MeshRouterRTLCtrl
#-----------------------------------------------------------------------
class MeshRouterRTLCtrl( Model ):

  #---------------------------------------------------------------------
  # __init__
  #---------------------------------------------------------------------
  def __init__( s, id_, nrouters, nmessages, payload_nbits, nentries ):

    s.id_           = id_
    s.nrouters      = nrouters
    s.nmessages     = nmessages
    s.payload_nbits = payload_nbits
    s.nentries      = nentries

    s.msg_type      = NetMsg( nrouters, nmessages, payload_nbits )

    #-------------------------------------------------------------------
    # Interface
    #-------------------------------------------------------------------

    s.c2d = [ CtrlBundle( s.msg_type ) for x in xrange(5) ]

  #---------------------------------------------------------------------
  # elaborate_logic
  #---------------------------------------------------------------------
  def elaborate_logic( s ):

    s.arbiters = RoundRobinArbiterEn[ 5 ]( 5 )
    s.routes   = RouteCompute[ 5 ]( s.id_, s.nrouters )

    for i in xrange( 5 ):
      s.connect( s.arbiters[i].en, s.c2d[i].outbuf_rdy     )
      s.connect( s.routes[i].dest, s.c2d[i].inbuf_msg.dest )

    @s.combinational
    def arb_req():

      for i in range( 5 ):

        # Set arbiter requests

        s.arbiters[i].reqs[0].value = s.c2d[0].inbuf_val and s.routes[0].route[i]
        s.arbiters[i].reqs[1].value = s.c2d[1].inbuf_val and s.routes[1].route[i]
        s.arbiters[i].reqs[2].value = s.c2d[2].inbuf_val and s.routes[2].route[i]
        s.arbiters[i].reqs[3].value = s.c2d[3].inbuf_val and s.routes[3].route[i]
        s.arbiters[i].reqs[4].value = s.c2d[4].inbuf_val and s.routes[4].route[i]

    @s.combinational
    def set_ctrl_signals():

      for i in range( 5 ):

        # Set outbuf valid

        s.c2d[i].outbuf_val.value = s.arbiters[i].grants > 0

        # Set inbuf rdy

        s.c2d[i].inbuf_rdy.value = reduce_or(
          concat(
             s.arbiters[0].grants[i],
             s.arbiters[1].grants[i],
             s.arbiters[2].grants[i],
             s.arbiters[3].grants[i],
             s.arbiters[4].grants[i],
          )
        )

        # Set xbar select

        if   s.arbiters[i].grants == 0b00001: s.c2d[i].xbar_sel.value = 0
        elif s.arbiters[i].grants == 0b00010: s.c2d[i].xbar_sel.value = 1
        elif s.arbiters[i].grants == 0b00100: s.c2d[i].xbar_sel.value = 2
        elif s.arbiters[i].grants == 0b01000: s.c2d[i].xbar_sel.value = 3
        elif s.arbiters[i].grants == 0b10000: s.c2d[i].xbar_sel.value = 4
        else                                : s.c2d[i].xbar_sel.value = 0


#=======================================================================
# CtrlDpathBundle
#=======================================================================
class CtrlDpathBundle( PortBundle ):
  def __init__( s, msg_type ):

    # Control signals (ctrl -> dpath)
    s.inbuf_msg  = InPort ( msg_type )
    s.inbuf_val  = InPort ( 1 )
    s.inbuf_rdy  = OutPort( 1 )
    s.xbar_sel   = OutPort( 3 )
    s.outbuf_val = OutPort( 1 )
    s.outbuf_rdy = InPort ( 1 )

CtrlBundle, DpathBundle = create_PortBundles( CtrlDpathBundle )

#=======================================================================
# RouteCompute
#=======================================================================
# Dimension-ordered (x then y) routing module.
class RouteCompute( Model ):

  NORTH = 0b00001
  EAST  = 0b00010
  SOUTH = 0b00100
  WEST  = 0b01000
  TERM  = 0b10000

  def __init__( s, id_, nrouters ):

    s.xnodes = int( sqrt( nrouters ) )
    s.x      = id_ % s.xnodes
    s.y      = id_ / s.xnodes
    nbits    = get_sel_nbits( nrouters )

    s.dest  = InPort ( nbits )
    s.route = OutPort( 5 )

  def elaborate_logic( s ):

    s.x_dest = Wire( s.dest.nbits )
    s.y_dest = Wire( s.dest.nbits )

    @s.combinational
    def logic():

      # TODO: bitwidth inference for % and / don't work
      s.x_dest.value = s.dest % s.xnodes
      s.y_dest.value = s.dest / s.xnodes

      if   s.x_dest < s.x: s.route.value = s.WEST
      elif s.x_dest > s.x: s.route.value = s.EAST
      elif s.y_dest < s.y: s.route.value = s.NORTH
      elif s.y_dest > s.y: s.route.value = s.SOUTH
      else:
        assert s.x_dest == s.x
        assert s.y_dest == s.y
        s.route.value = s.TERM

