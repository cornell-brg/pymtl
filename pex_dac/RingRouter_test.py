#=========================================================================
# Queue Test Suite
#=========================================================================

from pymtl import *

import pmlib
from   pmlib.adapters import ValRdyToValCredit
from   pmlib.adapters import ValCreditToValRdy

from RingRouter  import RingRouter

from math import ceil, log

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness (Model):

  def __init__( self, id, num_nodes, src_msgs, sink_msgs,
                src_delay, sink_delay ):

    # Parameters

    credits = 3  # TODO: this is hardcoded in RingRouter, fix later
    msg = pmlib.net_msgs.NetMsgParams( num_nodes, 2, 8 )

    # Instantiate models

    self.router = RingRouter( id, num_nodes, 8 )

    self.src  = []
    self.v2c  = []
    self.c2v  = []
    self.sink = []
    for i in range(3):
      self.src  += [ pmlib.TestSource ( msg.nbits, src_msgs[i],  src_delay  ) ]
      self.v2c  += [ ValRdyToValCredit( msg.nbits, credits )               ]
      self.c2v  += [ ValCreditToValRdy( msg.nbits, credits )               ]
      self.sink += [ pmlib.TestSink   ( msg.nbits, sink_msgs[i], sink_delay ) ]

    # TODO: why aren't the src's getting proper names with IDX suffix?

    # Connect modules

    for i in range( 3 ):
      connect( self.src[i].out_msg,        self.v2c[i].from_msg     )
      connect( self.src[i].out_val,        self.v2c[i].from_val     )
      connect( self.src[i].out_rdy,        self.v2c[i].from_rdy     )

      connect( self.v2c[i].to_msg,         self.router.in_msg[i]    )
      connect( self.v2c[i].to_val,         self.router.in_val[i]    )
      connect( self.v2c[i].to_credit,      self.router.in_credit[i] )

      connect( self.router.out_msg[i],     self.c2v[i].from_msg     )
      connect( self.router.out_val[i],     self.c2v[i].from_val     )
      connect( self.router.out_credit[i],  self.c2v[i].from_credit  )

      connect( self.c2v[i].to_msg,         self.sink[i].in_msg      )
      connect( self.c2v[i].to_val,         self.sink[i].in_val      )
      connect( self.c2v[i].to_rdy,         self.sink[i].in_rdy      )


  def done( self ):
    all_done = True
    for i in range( 3 ):
      all_done = all_done and self.src[i].done.value and self.sink[i].done.value
    return all_done

  def line_trace( self ):
    # TODO: only line tracing one port
    trace = ''

    for i in range( 3 ):
      trace += self.v2c[i].line_trace() + ' '

    trace += '|| ' + self.router.line_trace() + ' ||'

    for i in range( 3 ):
      trace += self.c2v[i].line_trace() + ' '

    return trace

#-------------------------------------------------------------------------
# Run test
#-------------------------------------------------------------------------

def run_router_test( dump_vcd, vcd_file_name, id, num_nodes,
                     src_delay, sink_delay, test_msgs ):

  params = pmlib.net_msgs.NetMsgParams( num_nodes, 2, 8 )

  src_msgs  = [[], [], []]
  sink_msgs = [[], [], []]
  for test in test_msgs:
    dest     = test[0]
    src      = test[1]
    payload  = test[2]
    sink_idx = route( dest, id, num_nodes )

    msg = params.mk_msg( dest, src, 0, payload )
    src_msgs[ src ]       += [ msg ]
    sink_msgs[ sink_idx ] += [ msg ]

  # Instantiate and elaborate the model

  model = TestHarness( id, num_nodes, src_msgs, sink_msgs,
                       src_delay, sink_delay )
  model.elaborate()

  #print_connections( model.v2c[0] )

  # Create a simulator using the simulation tool

  sim = SimulationTool( model )
  if dump_vcd:
    sim.dump_vcd( vcd_file_name )

  # Run the simulation

  print ""

  sim.reset()
  while not model.done() and sim.num_cycles < 20:
    sim.print_line_trace()
    sim.cycle()

  assert model.done()

  # Add a couple extra ticks so that the VCD dump is nicer

  sim.cycle()
  sim.cycle()
  sim.cycle()

#-------------------------------------------------------------------------
# Utility Functions
#-------------------------------------------------------------------------

WEST = 0
TERM = 1
EAST = 2

def route( dest, id, nodes ):

  if ( dest < id ):
    dist_east = dest + ( nodes - id )
    dist_west = id - dest
  else:
    dist_east = dest - id
    dist_west = id + ( nodes - dest )

  if ( dest == id ):
    return TERM
  elif ( dist_east < dist_west ):
    return EAST
  else:
    return WEST

#-------------------------------------------------------------------------
# 4 Node Ring, Router 0
#-------------------------------------------------------------------------

def test_rr_0_4_d0( dump_vcd ):
  run_router_test( dump_vcd, "pex-dac-RingRouter-0-4-d0.vcd", 0, 4 ,0, 0,
                   [ #  dest  src     payload
                     [  0,    WEST,   0x01  ],
                     [  0,    TERM,   0x02  ],
                     [  0,    EAST,   0x03  ],
                     #[  0,    WEST,   0x01  ],
                     #[  1,    TERM,   0x02  ],
                     #[  2,    EAST,   0x03  ],
                     #[  1,    WEST,   0x04  ],
                     #[  1,    TERM,   0x05  ],
                     #[  1,    EAST,   0x06  ],
                     #[  2,    WEST,   0x07  ],
                     #[  2,    TERM,   0x08  ],
                     #[  2,    EAST,   0x09  ],
                     #[  3,    WEST,   0x0A  ],
                     #[  3,    TERM,   0x0B  ],
                     #[  3,    EAST,   0x0C  ],
                   ])


