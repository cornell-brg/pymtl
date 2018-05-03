#=========================================================================
# TestSynchronizer
#=========================================================================
# Every synchronizer should have a unique index starting with 0. The
# synchronizers also share a synch_table between them by reference. The
# format of the synch_table is as follows:
#
# synch_table = [ [ [ src0_synch_tokens, src0_token_ctr ],
#                   [ src1_synch_tokens, src1_token_ctr ], ... ],
#                 [ src0_synch_tokens, src0_token_ctr ],
#                   [ src1_synch_tokens, src1_token_ctr ], ... ],
#                 ..., ]
#
# E.g., if there are two synchronizers, the initial state of the
# synch_table might look like the following:
#
# synch_table = [ [ [ 3, 0 ], [ 5, 0 ], ],
#                 [ [ 0, 0 ], [ 1, 0 ], ],
#                 [ [ 2, 0 ], [ 2, 0 ], ], ]
#
# src0 and src1 are allowed 3 and 5 tokens respectively before the
# synchronization point. After some cycles, assume src0 and src1 had 3 and
# 2 tokens gone through. The synch_table now looks like the following:
#
# synch_table = [ [ [ 3, 3 ], [ 5, 2 ], ],
#                 [ [ 0, 0 ], [ 1, 0 ], ],
#                 [ [ 2, 0 ], [ 2, 0 ], ], ]
#
# Since src0 at this point completed all requests until the
# synchronization point, it is not allowed to continue until src1 also
# completes its 5 tokens required until the synchronization point. Once
# all synchronizers complete the number of tokens, they will all proceed
# to the next synchronization point.

from pymtl      import *
from pclib.ifcs import InValRdyBundle, OutValRdyBundle

class TestSynchInfo( object ):
  def __init__( self, synch_table ):
    self.synch_table = synch_table
    self.synch_idx = 0

  def can_send_more_tokens( self, idx ):
    # If we don't have any more synchronization points, we can send more
    # tokens.
    if self.synch_idx >= len( self.synch_table ):
      return True

    # Otherwise, we need to check if we are allowed to send more.
    synch_tokens, token_ctr = self.synch_table[ self.synch_idx ][ idx ]
    return token_ctr < synch_tokens

  def token_sent( self, idx ):
    # Nothing to do if we don't have any more synchronization points.
    if self.synch_idx >= len( self.synch_table ):
      return

    self.synch_table[ self.synch_idx ][ idx ][ 1 ] += 1

    # Check if all synchronizers are satisfied, then increment the index.
    for synch_tokens, token_ctr in self.synch_table[ self.synch_idx ]:
      if token_ctr < synch_tokens:
        break

    else:
      self.synch_idx += 1

  def line_trace( self ):
    if self.synch_idx < len( self.synch_table ):
      row = self.synch_table[ self.synch_idx ]
    else:
      row = []
    return "{}:{}".format( self.synch_idx, row )

class TestSynchronizer( Model ):

  def __init__( s, dtype, idx, synch_info ):

    s.in_ = InValRdyBundle( dtype )
    s.out = OutValRdyBundle( dtype )
    s.connect( s.out.msg, s.in_.msg )

    s.num_cycles = Wire( 32 )

    @s.combinational
    def comb():
      # PyMTL sensitivity bug... Force this combinational block to be
      # fired every cycle.
      _ = s.num_cycles

      if synch_info.can_send_more_tokens( idx ):
        s.in_.rdy.value = s.out.rdy
        s.out.val.value = s.in_.val

      else:
        s.in_.rdy.value = 0
        s.out.val.value = 0

    @s.tick
    def tick():
      if s.out.val and s.out.rdy:
        synch_info.token_sent( idx )

      s.num_cycles.next = s.num_cycles + 1


