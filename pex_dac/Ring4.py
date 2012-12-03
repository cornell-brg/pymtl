#=========================================================================
# Ring
#=========================================================================

from   pymtl import *
import pmlib

from math import ceil, log

from pmlib.net_msgs import NetMsgParams
from RingRouter     import RingRouter

class Ring4 (Model):

  def __init__( s ):

    # Local Parameters
    num_routers    = 4
    num_messages   = 16
    payload_nbits  = 26
    num_entries    = 8
    netmsg_params  = NetMsgParams( num_routers, num_messages, payload_nbits )
    s.netmsg       = netmsg_params

    #---------------------------------------------------------------------
    # Interface Ports
    #---------------------------------------------------------------------

    s.in_msg    = [ InPort  ( netmsg_params.nbits ) for x in xrange( num_routers ) ]
    s.in_val    = [ InPort  ( 1 ) for x in xrange( num_routers ) ]
    s.in_credit = [ OutPort ( 1 ) for x in xrange( num_routers ) ]

    s.out_msg    = [ OutPort ( netmsg_params.nbits ) for x in xrange(num_routers ) ]
    s.out_val    = [ OutPort ( 1 ) for x in xrange( num_routers ) ]
    s.out_credit = [ InPort  ( 1 ) for x in xrange( num_routers ) ]

    #---------------------------------------------------------------------
    # Static elaboration
    #---------------------------------------------------------------------

    # Instantiate Routers

    s.routers = [ RingRouter( x, num_routers, num_messages,
                              payload_nbits, num_entries )
                  for x in xrange( num_routers ) ]


    # connect input/output terminals

    for i in xrange( num_routers ):


      connect( s.in_msg[i],             s.routers[i].in_msg[0]    )
      connect( s.in_val[i],             s.routers[i].in_val[0]    )
      connect( s.in_credit[i],          s.routers[i].in_credit[0] )

      connect( s.routers[i].out_msg[0],     s.out_msg[i]    )
      connect( s.routers[i].out_val[0],     s.out_val[i]    )
      connect( s.routers[i].out_credit[0],  s.out_credit[i] )

    # connect ring

    connect( s.routers[0].in_msg[1],     s.routers[num_routers - 1].out_msg[2]    )
    connect( s.routers[0].in_val[1],     s.routers[num_routers - 1].out_val[2]    )
    connect( s.routers[0].in_credit[1],  s.routers[num_routers - 1].out_credit[2] )

    connect( s.routers[0].out_msg[1],    s.routers[num_routers - 1].in_msg[2]    )
    connect( s.routers[0].out_val[1],    s.routers[num_routers - 1].in_val[2]    )
    connect( s.routers[0].out_credit[1], s.routers[num_routers - 1].in_credit[2] )

    for i in xrange( 0, num_routers - 1 ):

      connect( s.routers[i].in_msg[2],     s.routers[i + 1].out_msg[1]    )
      connect( s.routers[i].in_val[2],     s.routers[i + 1].out_val[1]    )
      connect( s.routers[i].in_credit[2],  s.routers[i + 1].out_credit[1] )

      connect( s.routers[i].out_msg[2],    s.routers[i + 1].in_msg[1]     )
      connect( s.routers[i].out_val[2],    s.routers[i + 1].in_val[1]     )
      connect( s.routers[i].out_credit[2], s.routers[i + 1].in_credit[1]  )

  #-----------------------------------------------------------------------
  # Line tracing
  #-----------------------------------------------------------------------

  def line_trace( self ):

    seqnum = self.netmsg.seqnum_slice

    def trace( val, msg ):
      if val:
        return '{}'.format( msg[ seqnum ].uint )
      else:
        return ' '

    def one_router( r ):
      term = "{}{}{}{}".format( trace( r.in_val[0].value, r.in_msg[0].value ),
                                '+' if r.in_credit[0].value else ' ',
                                trace( r.out_val[0].value, r.out_msg[0].value ),
                                '+' if r.out_credit[0].value else ' ' )

      west = "{}{}{}{}".format( trace( r.in_val[1].value, r.in_msg[1].value ),
                                '+' if r.in_credit[1].value else ' ',
                                trace( r.out_val[1].value, r.out_msg[1].value ),
                                '+' if r.out_credit[1].value else ' ' )

      east = "{}{}{}{}".format( trace( r.in_val[2].value, r.in_msg[2].value ),
                                '+' if r.in_credit[2].value else ' ',
                                trace( r.out_val[2].value, r.out_msg[2].value ),
                                '+' if r.out_credit[2].value else ' ' )

      return ' ' + west + term + east + ' |'

    s = ''
    for router in self.routers:
      s += one_router( router )

    return  s


