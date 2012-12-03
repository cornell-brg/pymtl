#=========================================================================
# RingRouter
#=========================================================================

from pymtl import *
import pmlib

from pmlib.net_msgs    import NetMsgParams
from NormalQueue       import NormalQueue
from pmlib.queues      import SingleElementPipelinedQueue
from InputTerminalCtrl import InputTerminalCtrl
from InputCtrl         import InputCtrl
from RingOutputCtrl    import RingOutputCtrl
from Crossbar3         import Crossbar3

from math import ceil, log

class RingRouterCtrl (Model):

  @capture_args
  def __init__( s, router_id, num_routers,  num_messages,
    payload_nbits, num_entries ):

    # Local Parameters

    credit_nbits    = int( ceil( log( num_entries+1, 2 ) ) )
    s.netmsg_params = NetMsgParams( num_routers, num_messages, payload_nbits )

    #---------------------------------------------------------------------
    # Interface Ports
    #---------------------------------------------------------------------

    # Port 0 - Terminal

    s.dest0         = InPort  ( s.netmsg_params.srcdest_nbits )
    s.in0_deq_val   = InPort  ( 1 )
    s.in0_deq_rdy   = OutPort ( 1 )
    s.in0_credit    = OutPort ( 1 )
    s.out0_val      = OutPort ( 1 )
    s.xbar_sel0     = OutPort ( 2 )
    s.out0_credit   = InPort  ( 1 )

    # Port 1 - West

    s.dest1         = InPort  ( s.netmsg_params.srcdest_nbits )
    s.in1_deq_val   = InPort  ( 1 )
    s.in1_deq_rdy   = OutPort ( 1 )
    s.in1_credit    = OutPort ( 1 )
    s.out1_val      = OutPort ( 1 )
    s.xbar_sel1     = OutPort ( 2 )
    s.out1_credit   = InPort  ( 1 )

    # Port 2 - East

    s.dest2         = InPort  ( s.netmsg_params.srcdest_nbits )
    s.in2_deq_val   = InPort  ( 1 )
    s.in2_deq_rdy   = OutPort ( 1 )
    s.in2_credit    = OutPort ( 1 )
    s.out2_val      = OutPort ( 1 )
    s.xbar_sel2     = OutPort ( 2 )
    s.out2_credit   = InPort  ( 1 )

    #---------------------------------------------------------------------
    # Static elaboration
    #---------------------------------------------------------------------

    # InputCtrl - Terminal Port

    s.inctrl_term = m = InputTerminalCtrl( router_id, num_routers,
                          s.netmsg_params.srcdest_nbits, credit_nbits, num_entries )
    connect({
      m.dest      : s.dest0,
      m.deq_val   : s.in0_deq_val,
      m.deq_rdy   : s.in0_deq_rdy,
      m.in_credit : s.in0_credit,
    })

    # InputCtrl - West Port

    s.inctrl_west = m = InputCtrl( router_id, num_routers,
                          s.netmsg_params.srcdest_nbits, credit_nbits, num_entries )
    connect({
      m.dest      : s.dest1,
      m.deq_val   : s.in1_deq_val,
      m.deq_rdy   : s.in1_deq_rdy,
      m.in_credit : s.in1_credit,
    })

    # InputCtrl - East Port

    s.inctrl_east = m = InputCtrl( router_id, num_routers,
                          s.netmsg_params.srcdest_nbits, credit_nbits, num_entries )
    connect({
      m.dest      : s.dest2,
      m.deq_val   : s.in2_deq_val,
      m.deq_rdy   : s.in2_deq_rdy,
      m.in_credit : s.in2_credit,
    })

    # Output Ctrl - Terminal Port

    s.outctrl_term = m = RingOutputCtrl( num_entries,
                           credit_nbits )
    connect({
      m.credit   : s.out0_credit,
      m.xbar_sel : s.xbar_sel0,
      m.out_val  : s.out0_val
    })

    # Output Ctrl - West Port

    s.outctrl_west = m = RingOutputCtrl(  num_entries,
                           credit_nbits )
    connect({
      m.credit   : s.out1_credit,
      m.xbar_sel : s.xbar_sel1,
      m.out_val  : s.out1_val
    })

    # Output Ctrl - East Port

    s.outctrl_east = m = RingOutputCtrl(  num_entries,
                           credit_nbits )
    connect({
      m.credit   : s.out2_credit,
      m.xbar_sel : s.xbar_sel2,
      m.out_val  : s.out2_val
    })

    # credit count connections

    connect( s.inctrl_term.out1_credit_cnt, s.outctrl_west.credit_count  )
    connect( s.inctrl_term.out2_credit_cnt, s.outctrl_east.credit_count  )

    # requests / grants connections

    connect( s.outctrl_term.reqs[0], s.inctrl_term.reqs[0] )
    connect( s.outctrl_term.reqs[1], s.inctrl_west.reqs[0] )
    connect( s.outctrl_term.reqs[2], s.inctrl_east.reqs[0] )

    connect( s.outctrl_west.reqs[0], s.inctrl_term.reqs[1] )
    connect( s.outctrl_west.reqs[1], s.inctrl_west.reqs[1] )
    connect( s.outctrl_west.reqs[2], s.inctrl_east.reqs[1] )

    connect( s.outctrl_east.reqs[0], s.inctrl_term.reqs[2] )
    connect( s.outctrl_east.reqs[1], s.inctrl_west.reqs[2] )
    connect( s.outctrl_east.reqs[2], s.inctrl_east.reqs[2] )

    connect( s.inctrl_term.grants[0], s.outctrl_term.grants[0] )
    connect( s.inctrl_term.grants[1], s.outctrl_west.grants[0] )
    connect( s.inctrl_term.grants[2], s.outctrl_east.grants[0] )

    connect( s.inctrl_west.grants[0], s.outctrl_term.grants[1] )
    connect( s.inctrl_west.grants[1], s.outctrl_west.grants[1] )
    connect( s.inctrl_west.grants[2], s.outctrl_east.grants[1] )

    connect( s.inctrl_east.grants[0], s.outctrl_term.grants[2] )
    connect( s.inctrl_east.grants[1], s.outctrl_west.grants[2] )
    connect( s.inctrl_east.grants[2], s.outctrl_east.grants[2] )

class RingRouterDpath (Model):

  @capture_args
  def __init__( s, router_id, num_routers, num_messages, payload_nbits, num_entries ):

    # Local Parameters
    s.netmsg_params = NetMsgParams( num_routers, num_messages, payload_nbits )

    #---------------------------------------------------------------------
    # Interface Ports
    #---------------------------------------------------------------------

    # Port 0 - Terminal

    s.in0_enq_msg   = InPort  ( s.netmsg_params.nbits )
    s.in0_enq_val   = InPort  ( 1 )

    s.in0_dest      = OutPort ( s.netmsg_params.srcdest_nbits )
    s.in0_deq_val   = OutPort ( 1 )
    s.in0_deq_rdy   = InPort  ( 1 )

    s.xbar_sel0     = InPort  ( 2 )
    s.out0_enq_val  = InPort  ( 1 )
    s.out0_deq_msg  = OutPort ( s.netmsg_params.nbits )
    s.out0_deq_val  = OutPort ( 1 )

    # Port 1 - West

    s.in1_enq_msg   = InPort  ( s.netmsg_params.nbits )
    s.in1_enq_val   = InPort  ( 1 )

    s.in1_dest      = OutPort ( s.netmsg_params.srcdest_nbits )
    s.in1_deq_val   = OutPort ( 1 )
    s.in1_deq_rdy   = InPort  ( 1 )

    s.xbar_sel1     = InPort  ( 2 )
    s.out1_enq_val  = InPort  ( 1 )
    s.out1_deq_msg  = OutPort ( s.netmsg_params.nbits )
    s.out1_deq_val  = OutPort ( 1 )

    # Port 2 - East

    s.in2_enq_msg   = InPort  ( s.netmsg_params.nbits )
    s.in2_enq_val   = InPort  ( 1 )

    s.in2_dest      = OutPort ( s.netmsg_params.srcdest_nbits )
    s.in2_deq_val   = OutPort ( 1 )
    s.in2_deq_rdy   = InPort  ( 1 )

    s.xbar_sel2     = InPort  ( 2 )
    s.out2_enq_val  = InPort  ( 1 )
    s.out2_deq_msg  = OutPort ( s.netmsg_params.nbits )
    s.out2_deq_val  = OutPort ( 1 )

    #---------------------------------------------------------------------
    # Static elaboration
    #---------------------------------------------------------------------

    # Input Queues

    # terminal
    s.in0_queue = m = NormalQueue( nbits= s.netmsg_params.nbits )
    connect({
      m.enq_bits         : s.in0_enq_msg,
      m.enq_val          : s.in0_enq_val,
      m.deq_val          : s.in0_deq_val,
      m.deq_rdy          : s.in0_deq_rdy
    })

    connect( s.in0_queue.deq_bits[ s.netmsg_params.dest_slice ], s.in0_dest )

    # west
    s.in1_queue = m = NormalQueue( nbits=s.netmsg_params.nbits )
    connect({
      m.enq_bits         : s.in1_enq_msg,
      m.enq_val          : s.in1_enq_val,
      m.deq_val          : s.in1_deq_val,
      m.deq_rdy          : s.in1_deq_rdy
    })

    connect( s.in1_queue.deq_bits[ s.netmsg_params.dest_slice ], s.in1_dest )

    # east
    s.in2_queue = m = NormalQueue( nbits=s.netmsg_params.nbits )
    connect({
      m.enq_bits         : s.in2_enq_msg,
      m.enq_val          : s.in2_enq_val,
      m.deq_val          : s.in2_deq_val,
      m.deq_rdy          : s.in2_deq_rdy
    })

    connect( s.in2_queue.deq_bits[ s.netmsg_params.dest_slice ], s.in2_dest )

    # Crossbar

    s.crossbar = m = Crossbar3( router_id, nbits=s.netmsg_params.nbits )
    connect({
      m.in0 : s.in0_queue.deq_bits,
      m.sel0 : s.xbar_sel0,
      m.in1 : s.in1_queue.deq_bits,
      m.sel1 : s.xbar_sel1,
      m.in2 : s.in2_queue.deq_bits,
      m.sel2 : s.xbar_sel2,
    })

    # Channel piped queues

    # terminal
    s.out0_q = m = SingleElementPipelinedQueue( s.netmsg_params.nbits )
    connect({
      m.enq_bits : s.crossbar.out0,
      m.enq_val  : s.out0_enq_val,
      m.deq_bits : s.out0_deq_msg,
      m.deq_val  : s.out0_deq_val,
      m.deq_rdy  : 1
    })

    # west
    s.out1_q = m = SingleElementPipelinedQueue( s.netmsg_params.nbits )
    connect({
      m.enq_bits : s.crossbar.out1,
      m.enq_val  : s.out1_enq_val,
      m.deq_bits : s.out1_deq_msg,
      m.deq_val  : s.out1_deq_val,
      m.deq_rdy  : 1
    })

    # east
    s.out2_q = m = SingleElementPipelinedQueue( s.netmsg_params.nbits )
    connect({
      m.enq_bits : s.crossbar.out2,
      m.enq_val  : s.out2_enq_val,
      m.deq_bits : s.out2_deq_msg,
      m.deq_val  : s.out2_deq_val,
      m.deq_rdy  : 1
    })

class RingRouter (Model):

  @capture_args
  def __init__( s, router_id, num_routers, num_messages, payload_nbits, num_entries ):

    # Local Parameters

    s.netmsg_params = NetMsgParams( num_routers, num_messages, payload_nbits )

    #---------------------------------------------------------------------
    # Interface Ports
    #---------------------------------------------------------------------

    s.in_msg     = [ InPort  ( s.netmsg_params.nbits ) for x in xrange(3) ]
    s.in_val     = [ InPort  ( 1 ) for x in xrange(3) ]
    s.in_credit  = [ OutPort ( 1 ) for x in xrange(3) ]
    s.out_credit = [ InPort  ( 1 ) for x in xrange(3) ]
    s.out_msg    = [ OutPort ( s.netmsg_params.nbits ) for x in xrange(3) ]
    s.out_val    = [ OutPort ( 1 ) for x in xrange(3) ]

    #---------------------------------------------------------------------
    # Static elaboration
    #---------------------------------------------------------------------

    s.ctrl  = RingRouterCtrl  ( router_id, num_routers,
                num_messages, payload_nbits, num_entries )
    s.dpath = RingRouterDpath ( router_id, num_routers,
                num_messages, payload_nbits, num_entries )

    # ctrl unit connections

    connect( s.ctrl.in0_credit,  s.in_credit[0]  )
    connect( s.ctrl.out0_credit, s.out_credit[0] )
    connect( s.ctrl.in1_credit,  s.in_credit[1]  )
    connect( s.ctrl.out1_credit, s.out_credit[1] )
    connect( s.ctrl.in2_credit,  s.in_credit[2]  )
    connect( s.ctrl.out2_credit, s.out_credit[2] )

    # dpath unit connections

    connect( s.dpath.in0_enq_msg,  s.in_msg[0]  )
    connect( s.dpath.in0_enq_val,  s.in_val[0]  )
    connect( s.dpath.out0_deq_msg, s.out_msg[0] )
    connect( s.dpath.out0_deq_val, s.out_val[0] )
    connect( s.dpath.in1_enq_msg,  s.in_msg[1]  )
    connect( s.dpath.in1_enq_val,  s.in_val[1]  )
    connect( s.dpath.out1_deq_msg, s.out_msg[1] )
    connect( s.dpath.out1_deq_val, s.out_val[1] )
    connect( s.dpath.in2_enq_msg,  s.in_msg[2]  )
    connect( s.dpath.in2_enq_val,  s.in_val[2]  )
    connect( s.dpath.out2_deq_msg, s.out_msg[2] )
    connect( s.dpath.out2_deq_val, s.out_val[2] )

    # control signal connections (ctrl -> dpath )

    connect( s.ctrl.in0_deq_rdy, s.dpath.in0_deq_rdy  )
    connect( s.ctrl.out0_val,    s.dpath.out0_enq_val )
    connect( s.ctrl.xbar_sel0,   s.dpath.xbar_sel0    )
    connect( s.ctrl.in1_deq_rdy, s.dpath.in1_deq_rdy  )
    connect( s.ctrl.out1_val,    s.dpath.out1_enq_val )
    connect( s.ctrl.xbar_sel1,   s.dpath.xbar_sel1    )
    connect( s.ctrl.in2_deq_rdy, s.dpath.in2_deq_rdy  )
    connect( s.ctrl.out2_val,    s.dpath.out2_enq_val )
    connect( s.ctrl.xbar_sel2,   s.dpath.xbar_sel2    )

    # status signal connections (ctrl <- dpath)

    connect( s.ctrl.in0_deq_val, s.dpath.in0_deq_val )
    connect( s.ctrl.dest0,       s.dpath.in0_dest    )
    connect( s.ctrl.in1_deq_val, s.dpath.in1_deq_val )
    connect( s.ctrl.dest1,       s.dpath.in1_dest    )
    connect( s.ctrl.in2_deq_val, s.dpath.in2_deq_val )
    connect( s.ctrl.dest2,       s.dpath.in2_dest    )
