#=========================================================================
# Torus
#=========================================================================

from   pymtl import *
import pmlib

from math import ceil, log, sqrt

from pmlib.net_msgs import NetMsgParams
from TorusRouter    import TorusRouter
from pmlib.adapters import ValRdyToValCredit, ValCreditToValRdy

class Torus (Model):

  def __init__( s, num_routers, num_messages, payload_nbits, num_entries ):

    # Local Parameters

    netmsg_params  = NetMsgParams( num_routers, num_messages, payload_nbits )
    s.netmsg       = netmsg_params
    num_routers_1D = int( sqrt( num_routers ) )

    #---------------------------------------------------------------------
    # Interface Ports
    #---------------------------------------------------------------------

    s.in_msg  = [ InPort  ( netmsg_params.nbits ) for x in xrange( num_routers ) ]
    s.in_val  = [ InPort  ( 1 ) for x in xrange( num_routers ) ]
    s.in_rdy  = [ OutPort ( 1 ) for x in xrange( num_routers ) ]

    s.out_msg = [ OutPort ( netmsg_params.nbits ) for x in xrange(num_routers ) ]
    s.out_val = [ OutPort ( 1 ) for x in xrange( num_routers ) ]
    s.out_rdy = [ InPort  ( 1 ) for x in xrange( num_routers ) ]

    #---------------------------------------------------------------------
    # Static elaboration
    #---------------------------------------------------------------------

    # Instantiate Routers

    s.routers = [ TorusRouter( x % num_routers_1D, x / num_routers_1D,
                    num_routers, num_messages, payload_nbits, num_entries )
                    for x in xrange( num_routers ) ]

    # Instantiate Channel Queues

    s.v2c = [ ValRdyToValCredit( netmsg_params.nbits, num_entries )
              for x in xrange( num_routers ) ]

    s.c2v = [ ValCreditToValRdy( netmsg_params.nbits, num_entries )
              for x in xrange( num_routers ) ]

    # connect input/output terminals

    for i in xrange( num_routers ):

      connect( s.in_msg[i],                 s.v2c[i].from_msg         )
      connect( s.in_val[i],                 s.v2c[i].from_val         )
      connect( s.in_rdy[i],                 s.v2c[i].from_rdy         )

      connect( s.v2c[i].to_msg,             s.routers[i].in_msg[4]    )
      connect( s.v2c[i].to_val,             s.routers[i].in_val[4]    )
      connect( s.v2c[i].to_credit,          s.routers[i].in_credit[4] )

      connect( s.routers[i].out_msg[4],     s.c2v[i].from_msg         )
      connect( s.routers[i].out_val[4],     s.c2v[i].from_val         )
      connect( s.routers[i].out_credit[4],  s.c2v[i].from_credit      )

      connect( s.c2v[i].to_msg,             s.out_msg[i]              )
      connect( s.c2v[i].to_val,             s.out_val[i]              )
      connect( s.c2v[i].to_rdy,             s.out_rdy[i]              )

    # connect torus

    for j in xrange( num_routers_1D ):
      for i in xrange( num_routers_1D ):

        # current router_id

        curr = i + j*num_routers_1D

        # east neighbor

        east = (i+1)%num_routers_1D + j*num_routers_1D

        # east<-west input connections

        connect( s.routers[curr].in_msg[1],     s.routers[east].out_msg[3]    )
        connect( s.routers[curr].in_val[1],     s.routers[east].out_val[3]    )
        connect( s.routers[curr].in_credit[1],  s.routers[east].out_credit[3] )

        # east->west output connections

        connect( s.routers[curr].out_msg[1],    s.routers[east].in_msg[3]     )
        connect( s.routers[curr].out_val[1],    s.routers[east].in_val[3]     )
        connect( s.routers[curr].out_credit[1], s.routers[east].in_credit[3]  )

        # south neighbor

        south = i + ( (j+1)%num_routers_1D ) * num_routers_1D

        # south<-north input connections

        connect( s.routers[curr].in_msg[2],    s.routers[south].out_msg[0]    )
        connect( s.routers[curr].in_val[2],    s.routers[south].out_val[0]    )
        connect( s.routers[curr].in_credit[2], s.routers[south].out_credit[0] )

        # south->north output connections

        connect( s.routers[curr].out_msg[2],    s.routers[south].in_msg[0]    )
        connect( s.routers[curr].out_val[2],    s.routers[south].in_val[0]    )
        connect( s.routers[curr].out_credit[2], s.routers[south].in_credit[0] )

  #-----------------------------------------------------------------------
  # Line tracing
  #-----------------------------------------------------------------------

  def line_trace( s ):

    seqnum = s.netmsg.seqnum_slice
    dest   = s.netmsg.dest_slice
    src    = s.netmsg.src_slice

    def trace( val, msg ):
      if val:
        return '{}{}{}'.format( msg[ src ].uint, msg[ dest ].uint, msg[ seqnum ].uint )
      else:
        return ' '

    def one_router( r ):

      south = "{}{}{}{}".format( trace( r.in_val[2].value, r.in_msg[2].value ),
                                '+' if r.in_credit[2].value else ' ',
                                trace( r.out_val[2].value, r.out_msg[2].value ),
                                '+' if r.out_credit[2].value else ' ' )

      north = "{}{}{}{}".format( trace( r.in_val[0].value, r.in_msg[0].value ),
                                '+' if r.in_credit[0].value else ' ',
                                trace( r.out_val[0].value, r.out_msg[0].value ),
                                '+' if r.out_credit[0].value else ' ' )

      west = "{}{}{}{}".format( trace( r.in_val[3].value, r.in_msg[3].value ),
                                '+' if r.in_credit[3].value else ' ',
                                trace( r.out_val[3].value, r.out_msg[3].value ),
                                '+' if r.out_credit[3].value else ' ' )

      term = "{}{}{}{}".format( trace( r.in_val[4].value, r.in_msg[4].value ),
                                '+' if r.in_credit[4].value else ' ',
                                trace( r.out_val[4].value, r.out_msg[4].value ),
                                '+' if r.out_credit[4].value else ' ' )

      east = "{}{}{}{}".format( trace( r.in_val[1].value, r.in_msg[1].value ),
                                '+' if r.in_credit[1].value else ' ',
                                trace( r.out_val[1].value, r.out_msg[1].value ),
                                '+' if r.out_credit[1].value else ' ' )

      return ' ' + north + east + south + west + ' |'

    str_ = ''
    for router in s.routers:
      str_ += one_router( router )

    return  str_

