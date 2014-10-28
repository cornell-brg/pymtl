#!/usr/bin/env python
#=========================================================================
# cffi_net.py [options] nrouters injection_rate ncycles
#=========================================================================
#
#  -h --help           Display this message
#  -v --verbose        Verbose mode
#
#  --kernel            Choose pymtl implementation (default v1)
#                       c  : pymtl v1 csim
#                       py : pymtl v1 pysim
#
#  --impl              Choose model implementation (default bl)
#                       bl  : behavioral level
#                       cl  : cycle level
#
#  --verify            Validate logic.
#
#  --elaborate_only    Only perform elaboration.
#
#  --profile           Use cProfile on the simulation.
#
#  --stats             Collect and dump simulator stats.
#
# Benchmark testing of a variable latency iterative multiplier.
#

import argparse
import sys
import random
import copy

from collections import deque
# TODO: currently only passing dest int, not a NetObject message!
#from new_pmlib   import NetMsg
#from NetObject   import NetObject

from pymtl import get_cpp
from cffi      import FFI

#-------------------------------------------------------------------------
# Constants
#-------------------------------------------------------------------------

NMESSAGES         = 2*16
PAYLOAD_NBITS     = 16
NENTRIES          = 4
INVALID_TIMESTAMP = 0

#-------------------------------------------------------------------------
# Command line processing
#-------------------------------------------------------------------------

class ArgumentParserWithCustomError(argparse.ArgumentParser):
  def error( self, msg = "" ):
    if ( msg ): print("\n ERROR: %s" % msg)
    print("")
    file = open( sys.argv[0] )
    for ( lineno, line ) in enumerate( file ):
      if ( line[0] != '#' ): sys.exit(msg != "")
      if ( (lineno == 2) or (lineno >= 4) ): print( line[1:].rstrip("\n") )

def parse_cmdline():
  p = ArgumentParserWithCustomError( add_help=False )

  p.add_argument( "-v", "--verbose",  action="store_true" )
  p.add_argument( "-h", "--help",     action="store_true" )

  p.add_argument( "--verify",         action="store_true" )
  p.add_argument( "--elaborate_only", action="store_true" )
  p.add_argument( "--profile",        action="store_true" )
  p.add_argument( "--stats",          action="store_true" )

  p.add_argument( "--kernel", default="py", choices=["c","py"] )

  p.add_argument( "--impl", default="bl", choices=["bl","cl"] )

  p.add_argument( "nrouters",       type=int )
  p.add_argument( "injection_rate", type=int )
  #p.add_argument( "npackets",       type=int )
  p.add_argument( "ncycles" ,       type=int )

  opts = p.parse_args()
  if opts.help: p.error()
  return opts

#-------------------------------------------------------------------------
# get_filename
#-------------------------------------------------------------------------
# Get the current filename.
def get_filename():
  from os.path import basename
  from os.path import splitext
  return splitext( basename( __file__ ) )[0]

#-------------------------------------------------------------------------
# mk_net_msg
#-------------------------------------------------------------------------
#mk_net_msg = NetObject
mk_net_msg = lambda a,b,c,d: a

#-------------------------------------------------------------------------
# srand/rand
#-------------------------------------------------------------------------
# Using C random allows verification against C implementations.
ffi = FFI()
ffi.cdef("""
  void srand( unsigned int seed );
  int  rand ( void );
""")
libc = ffi.dlopen(None)

#-------------------------------------------------------------------------
# verify
#-------------------------------------------------------------------------
def verify( model, sim, opts, dump_vcd, verbose ):

  # Simulation Variables

  packets_gen  = 0
  packets_recv = 0
  sim_done     = False

  # Message generator and source queues

  src        = [ deque() for x in xrange( opts.nrouters ) ]

  # Reset the simulator

  for i in xrange( opts.nrouters ):
    model.out[i].rdy.value = 1
  sim.reset()

  # Simulation loop
  puts = [ [] for x in range( opts.nrouters ) ]
  gets = [ [] for x in range( opts.nrouters ) ]
  seq = 0

  while sim.ncycles < opts.ncycles or packets_gen != packets_recv:
    for i in xrange( opts.nrouters ):

      # Generate packet and insert into source queue
      if  sim.ncycles < opts.ncycles and\
        ( random.randint( 0, 100 ) < opts.injection_rate ):

        # Create uniform random traffic
        dest = random.randint( 0, opts.nrouters-1 )
        msg  = mk_net_msg( dest, i, packets_gen, INVALID_TIMESTAMP )
        src[i].append( msg )
        packets_gen += 1

        puts[dest].append(msg)

      # Inject from source queue
      if ( len( src[i] ) > 0 ):
        model.in_[i].msg.value = src[i][0]
        model.in_[i].val.value = 1
      else:
        model.in_[i].val.value = 0

      # Receive a packet
      if ( model.out[i].val.value == 1 ):
        packets_recv += 1
        gets[i].append( copy.copy(model.out[i].msg.value) )

      # Pop the source queue
      if ( model.in_[i].rdy.value == 1 ) and ( len( src[i] ) > 0 ):
        src[i].popleft()

    # Increment simulator and print line trace
    #print sim.ncycles, ':', '-'*20
    sim.cycle()
    if verbose: sim.print_line_trace()

  for i, (x, y) in enumerate( zip( puts, gets ) ):
  #  x.sort( key = lambda x: x.seqnum )
  #  y.sort( key = lambda x: x.seqnum )
    assert x == y

  print "VERIFICATION SUCCESSFUL!"
  print "Packets Sent/Recv: {}/{}".format(packets_gen, packets_recv)

#-------------------------------------------------------------------------
# simulate
#-------------------------------------------------------------------------
def simulate( model, sim, opts, dump_vcd, verbose ):

  # Simulation Variables

  packets_gen  = 0
  packets_recv = 0
  sim_done     = False

  # Message generator and source queues

  src        = [ deque() for x in xrange( opts.nrouters ) ]

  # Reset the simulator

  for i in xrange( opts.nrouters ):
    model.out[i].rdy.value = 1
  sim.reset()

  # Simulation loop
  seq = 0

  while sim.ncycles < opts.ncycles:
    for i in xrange( opts.nrouters ):

      # Generate packet and insert into source queue
      #if ( random.randint( 0, 100 ) < opts.injection_rate ):
      if ( (libc.rand() % 100) < opts.injection_rate ):

        # Create uniform random traffic
        #dest = random.randint( 0, opts.nrouters-1 )
        dest = libc.rand() % opts.nrouters
        msg  = mk_net_msg( dest, i, packets_gen, INVALID_TIMESTAMP )
        src[i].append( msg )
        packets_gen += 1


      # Inject from source queue
      if ( len( src[i] ) > 0 ):
        model.in_[i].msg.value = src[i][0]
        model.in_[i].val.value = 1
      else:
        model.in_[i].val.value = 0

      # Receive a packet
      if ( model.out[i].val.value == 1 ):
        packets_recv += 1

      # Pop the source queue
      if ( model.in_[i].rdy.value == 1 ) and ( len( src[i] ) > 0 ):
        src[i].popleft()

    # Increment simulator and print line trace
    sim.cycle()
    if verbose: sim.print_line_trace()

    # Debug
    #if sim.ncycles % 100 == 1:
    #  print "{:4}: gen {:5} recv {:5}".format( sim.ncycles,
    #                                           packets_gen,
    #                                           packets_recv )

  print "Packets Sent/Recv: {}/{}".format(packets_gen, packets_recv)

#-------------------------------------------------------------------------
# test_py_func
#-------------------------------------------------------------------------
def test_func( model_class, sim_class, opts ):

  model = model_class( )
  if opts.kernel == 'c':
    model = get_cpp( model )
  print "Instantiation done..."

  model.elaborate()
  print "Elaboration done..."
  if opts.elaborate_only: return

  sim = sim_class( model )
  print "Simulator Creation done..."

  run = verify if opts.verify else simulate

  results = run ( model,                 # model
                  sim,                   # simulator
                  opts,                  # options
                  # TODO: opts.dump_vcd,
                  False,                 # dump_vcd
                  opts.verbose )         # verbose

  print "Simulation done! Executed: {} cycles".format( sim.ncycles )

#-------------------------------------------------------------------------
# main
#-------------------------------------------------------------------------
def main():

  # Parse commandline, set seed for reproducible results
  opts = parse_cmdline()
  #random.seed( 0x4750 )
  libc.srand( 0x4750 )

  from CycleApproximateSimpleCache  import SimulationTool   as sim_class
  from CycleApproximateSimpleCache  import Bits             as Bits
  from CycleApproximateSimpleCache  import CL_Cache         as model_class

  test_func( model_class, sim_class, opts )

main()
