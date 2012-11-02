#=========================================================================
# Round Robin Arbiter
#=========================================================================

from pymtl import *

class RoundRobinArbiter(Model):

  def __init__(self, nreqs = 2):

    self.nreqs  = nreqs

    self.reqs   = InPort  (nreqs)
    self.grants = OutPort (nreqs)

    self.priority    = Wire( nreqs )
    self.priority_en = Wire( 1     )

  @posedge_clk
  def seq(self):

    if self.reset.value:
      self.priority.next = 1
    elif self.priority_en.value:
      self.priority.next    = self.grants.value << 1
      self.priority.next[0] = self.grants.value[ self.nreqs - 1 ]

  @combinational
  def comb(self):

    nreqs = self.nreqs

    temp = 0
    for i in xrange( nreqs ):
      temp = self.grants.value[i] | temp
    self.priority_en.value = temp

    kills        = Bits( 2*nreqs + 1 )
    priority_int = Bits( 2*nreqs )
    reqs_int     = Bits( 2*nreqs )
    grants_int   = Bits( 2*nreqs )

    kills[0] = 1;
    priority_int[0:nreqs]       = self.priority.value
    priority_int[nreqs:2*nreqs] = 0
    reqs_int[0:nreqs]           = self.reqs.value
    reqs_int[nreqs:2*nreqs]     = self.reqs.value

    for i in range(2*nreqs):

      if priority_int[i]:
        grants_int[i] = reqs_int[i]
      else:
        grants_int[i] = ~kills[i] & reqs_int[i]

      if priority_int[i]:
        kills[i+1] = grants_int[i]
      else:
        kills[i+1] = kills[i] | grants_int[i]

    for i in range( nreqs ):
      self.grants[i].value = grants_int[i] | grants_int[nreqs+i]

  def line_trace(self):
    return "{:04b} | {:04b}".format( self.reqs.value.uint, self.grants.value.uint )


