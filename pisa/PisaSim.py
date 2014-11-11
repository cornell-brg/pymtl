#=========================================================================
# PisaSim
#=========================================================================
# Basic ISA simulator.
#
# Author : Christopher Batten
# Date   : May 22, 2014

import collections
import struct

from pymtl         import Bits
from pclib.fl      import Bytes
from PisaInst      import PisaInst
from PisaSemantics import PisaSemantics

from accel.mvmult.mvmult_fl import MatrixVec

class PisaSim (object):

  #-----------------------------------------------------------------------
  # Constructor
  #-----------------------------------------------------------------------

  def __init__( self, test_en=True, trace_en=False ):

    # If test mode is enabled, the the simulator assumes we will load the
    # reference output using a proc2mngr section in the sparse memory
    # image. If the simulator is not in test mode, then it assumes the
    # program will use use the following instruction to end the program:
    #
    #   mtc0 r1, proc2mngr
    #
    # The value written using this instruction will be available in the
    # return_value attribute.

    self.test_en = test_en
    self.status  = 0

    # If tracing is true then output line tracing

    self.trace_en = trace_en

    # Stats

    self.num_total_inst = 0
    self.num_inst = 0

    # Create the memory. For now we hard code the memory size to 1MB.

    self.mem = Bytes(2**20)

    # Create the proc/mngr queues

    self.mngr2proc_queue     = collections.deque()
    self.proc2mngr_queue     = collections.deque()
    self.proc2mngr_ref_queue = collections.deque()

    # Create the accelerator

    self.xcel_mvmult = MatrixVec( self.mem )

    # Construct the ISA semantics object

    self.isa = PisaSemantics( self.mem,
                              self.mngr2proc_queue,
                              self.proc2mngr_queue,
                              self.xcel_mvmult )

  #-----------------------------------------------------------------------
  # reset
  #-----------------------------------------------------------------------

  def reset( self ):

    self.isa.PC         = Bits( 32, 0x0000400 )
    self.isa.status     = 0

    self.status         = 0
    self.num_total_inst = 0
    self.num_inst       = 0

  #-----------------------------------------------------------------------
  # load
  #-----------------------------------------------------------------------

  def load( self, mem_image ):

    # Iterate over the sections

    sections = mem_image.get_sections()
    for section in sections:

      # For .mngr2proc sections, copy section into mngr2proc queue

      if section.name == ".mngr2proc":
        for i in xrange(0,len(section.data),4):
          bits = struct.unpack_from("<I",buffer(section.data,i,4))[0]
          self.mngr2proc_queue.append( Bits(32,bits) )

      # For .proc2mngr sections, copy section into proc2mngr_ref queue

      elif section.name == ".proc2mngr":
        for i in xrange(0,len(section.data),4):
          bits = struct.unpack_from("<I",buffer(section.data,i,4))[0]
          self.proc2mngr_ref_queue.append( Bits(32,bits) )

      # For all other sections, simply copy them into the memory

      else:
        start_addr = section.addr
        stop_addr  = section.addr + len(section.data)
        self.mem[start_addr:stop_addr] = section.data

  #-----------------------------------------------------------------------
  # run
  #-----------------------------------------------------------------------

  def run( self ):

    try:

      # Keep running as long as there are values in the proc2mngr queue

      if self.trace_en:
        print ""

      pc = 0
      done = False
      while not done:

        # Update instruction counts

        self.num_total_inst += 1
        if self.isa.stats_en:
          self.num_inst += 1

        # Fetch instruction

        pc = self.isa.PC.uint()
        inst = PisaInst( self.mem[ pc : pc+4 ] )

        # Save some state for tracing

        if self.trace_en:
          self.isa.mngr2proc_str = ' '*8
          self.isa.proc2mngr_str = ' '*8

        # Execute instruction

        self.isa.execute( inst )

        # Line tracing

        if self.trace_en:
          if self.test_en:
            print " {} > {:0>8x} {:<20} > {}" \
              .format( self.isa.mngr2proc_str, pc, inst, self.isa.proc2mngr_str )
          else:
            print " {:0>8x}  {:<20}" \
              .format( pc, inst )

        # Check the proc2mngr queue

        if self.test_en:
          if self.proc2mngr_queue:
            assert self.proc2mngr_queue[0] == self.proc2mngr_ref_queue[0]
            self.proc2mngr_queue.popleft()
            self.proc2mngr_ref_queue.popleft()
            done = not bool(self.proc2mngr_ref_queue)
        else:
          if self.isa.status != 0:
            self.status = self.isa.status
            done = True

    except:
      print "Unexpected error at PC={:0>8x}!".format(pc)
      raise

