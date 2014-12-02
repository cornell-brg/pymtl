#!/usr/bin/env python
#=======================================================================
# tile-sim [options]
#=======================================================================
#
#  -h --help           Display this message
#  -v --verbose        Verbose mode
#
#  --bmark <bmark-name> Choose benchmark to run
#                        vvadd      : vector-vector addition
#                        bsearch    : binary search
#                        cmult      : complex multiplication
#                        mfilter    : masked filter
#                        mvmult     : matrix-vector multiply
#                        mvmult-cp2 : matrix-vector multiply coprocessor
#
#  --dump-vcd          Dump vcd to dump.vcd
#  --dump-vcd <fname>  Dump vcd to given file name <fname>
#
#  --stats             Dump stats standard out
#  --stats <fname>     Dump stats to given file name <fname>
#
#  --test-verilog      Use verilog translated version of processor
#  --elaborate_only    Only perform elaboration
#
#
# The processor simulator. Provide the benchmark name to run the
# selected benchmark by choosing the processor implementation. Use
# --stats to display statistics about the simulation.
#

import argparse
import sys
import re
import random
import os

from   pymtl import *

from pclib.test   import SparseMemoryImage
from pclib.test   import TestMemory
from pclib.test   import TestProcManager
from pclib.ifaces import mem_msgs
from Tile         import Tile

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

  # Standard command line arguments

  p.add_argument( "-v", "--verbose", action="store_true" )
  p.add_argument( "-h", "--help",    action="store_true" )

  # Additional command line arguments for the simulator

  p.add_argument( "--bmark",
    choices=["vvadd","bsearch","cmult","mfilter","mvmult","mvmult-cp2"] )

  p.add_argument( "--dump-vcd", nargs='?',
                  default=False, const=os.path.basename( __file__ ) )

  p.add_argument( "--stats",    nargs='?', default=False, const="-" )

  p.add_argument( "--test-verilog",   action="store_true" )
  p.add_argument( "--elaborate_only", action="store_true" )

  opts = p.parse_args()
  if opts.help: p.error()
  return opts

#-------------------------------------------------------------------------
# Simulation harness
#-------------------------------------------------------------------------

class SimHarness( Model ):

  def __init__( s, ModelType, input_params, test_verilog ):

    # input_list parameters

    mem_delay       = input_params[0]
    sparse_mem_img  = input_params[1]

    cache = False

    # Instantiate models

    data_nbits = 128 if cache else 32

    memreq_params  = mem_msgs.MemReqParams( 32, data_nbits )
    memresp_params = mem_msgs.MemRespParams( data_nbits )

    s.tile     = ModelType( reset_vector   = 0x00000400,
                            mem_data_nbits = data_nbits )

    s.mem      = TestMemory( memreq_params, memresp_params, 2,
                             mem_delay, mem_nbytes=2**24  )

    s.proc_mgr = TestProcManager( s.mem, sparse_mem_img )

    if test_verilog:
      s.tile = get_verilated( s.tile )

  def elaborate_logic( s ):

    # Connect Manager Signals

    s.connect( s.proc_mgr.proc_go,     s.tile.go     )
    s.connect( s.proc_mgr.proc_status, s.tile.status )

    # Memory Request/Response Signals

    s.connect( s.tile.memreq [0], s.mem.reqs [0] )
    s.connect( s.tile.memresp[0], s.mem.resps[0] )
    s.connect( s.tile.memreq [1], s.mem.reqs [1] )
    s.connect( s.tile.memresp[1], s.mem.resps[1] )

  def done( s ):
    return s.proc_mgr.done.value

  def line_trace( s ):
    return s.tile.line_trace() + s.mem.line_trace()

#-------------------------------------------------------------------------
# Benchmarks
#-------------------------------------------------------------------------------

vmh_dir = '../ubmark/build/vmh/'

def ubmark_vvadd():
  bmark_file     = vmh_dir + 'ubmark-vvadd.vmh'
  mem_delay      = 0
  sparse_mem_img = SparseMemoryImage( vmh_filename = bmark_file )
  return [ mem_delay, sparse_mem_img ]

def ubmark_bsearch():
  bmark_file     = vmh_dir + 'ubmark-bin-search.vmh'
  mem_delay      = 0
  sparse_mem_img = SparseMemoryImage( vmh_filename = bmark_file )
  return [ mem_delay, sparse_mem_img ]

def ubmark_cmult():
  bmark_file     = vmh_dir + 'ubmark-cmplx-mult.vmh'
  mem_delay      = 0
  sparse_mem_img = SparseMemoryImage( vmh_filename = bmark_file )
  return [ mem_delay, sparse_mem_img ]

def ubmark_mfilter():
  bmark_file     = vmh_dir + 'ubmark-masked-filter.vmh'
  mem_delay      = 0
  sparse_mem_img = SparseMemoryImage( vmh_filename = bmark_file )
  return [ mem_delay, sparse_mem_img ]

def ubmark_mvmult():
  bmark_file     = vmh_dir + 'ubmark-mvmult.vmh'
  mem_delay      = 0
  sparse_mem_img = SparseMemoryImage( vmh_filename = bmark_file )
  return [ mem_delay, sparse_mem_img ]

def ubmark_mvmult_cp2():
  bmark_file     = vmh_dir + 'ubmark-mvmult-cp2.vmh'
  mem_delay      = 0
  sparse_mem_img = SparseMemoryImage( vmh_filename = bmark_file )
  return [ mem_delay, sparse_mem_img ]

#-----------------------------------------------------------------------
# main()
#-----------------------------------------------------------------------
def main():

  opts = parse_cmdline()

  # Determine which bmark to run

  bmarks_dict = {
    'vvadd'      : ubmark_vvadd(),
    'bsearch'    : ubmark_bsearch(),
    'cmult'      : ubmark_cmult(),
    'mfilter'    : ubmark_mfilter(),
    'mvmult'     : ubmark_mvmult(),
    'mvmult-cp2' : ubmark_mvmult_cp2(),
  }

  # Instantiate and elaborate the model

  model = SimHarness( Tile, bmarks_dict[ opts.bmark ], opts.test_verilog )
  model.elaborate()
  if opts.elaborate_only: return

  # Create a simulator using the simulation tool

  sim = SimulationTool( model )

  # Turn on vcd dumping

  if opts.dump_vcd:
    sim.dump_vcd( opts.dump_vcd )

  # Reset the simulator

  sim.reset()

  # Run the simulation

  num_cycles = 0
  sim.reset()
  while not model.done():
    if opts.verbose:
      sim.print_line_trace()
    sim.cycle()
    if model.tile.stats_en:
      num_cycles += 1

  if model.tile.status == 1: print "PASS!!!"
  else:                      print "FAIL!!!", model.tile.status

  if opts.verbose:
    sim.print_line_trace()

  # Handle stats, redirect output to standard out or a file
  # TODO: need to handle stats!!!

  if opts.stats:

    os = sys.stdout
    if opts.stats != "-":
      os = open( opts.stats, "w" )

    print >>os, "num_cycles          =", num_cycles
    print >>os, "num_insts           =", model.tile.num_insts

  # Add a couple extra ticks so that the VCD dump is nicer

  sim.cycle()
  sim.cycle()
  sim.cycle()

  print "Simulation done! Executed: {} cycles".format( sim.ncycles )

main()
