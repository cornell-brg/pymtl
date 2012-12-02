#=========================================================================
# Temporary Queue Class!
#=========================================================================

from pymtl import *
import pmlib

from RegisterFile import RegisterFile
from math import ceil, log

#-------------------------------------------------------------------------------
# Multi-Element Normal Queue
#-------------------------------------------------------------------------------

class NormalQueue ( Model ):

  @capture_args
  def __init__( self, nbits ):

    # TODO: add check to prevent instantiation of single element queue

    # Interface Ports

    self.enq_bits = InPort  ( nbits )
    self.enq_val  = InPort  ( 1 )
    self.enq_rdy  = OutPort ( 1 )

    self.deq_bits = OutPort ( nbits )
    self.deq_val  = OutPort ( 1 )
    self.deq_rdy  = InPort  ( 1 )

    # Ctrl and Dpath unit instantiation

    self.ctrl  = NormalQueueCtrl( nbits )
    self.dpath = NormalQueueDpath( nbits )

    # Ctrl unit connections

    connect( self.ctrl.enq_val, self.enq_val )
    connect( self.ctrl.enq_rdy, self.enq_rdy )
    connect( self.ctrl.deq_val, self.deq_val )
    connect( self.ctrl.deq_rdy, self.deq_rdy )

    # Dpath unit connections

    connect( self.dpath.enq_bits, self.enq_bits )
    connect( self.dpath.deq_bits, self.deq_bits )

    # Control Signal connections (ctrl -> dpath)

    connect( self.dpath.wen,      self.ctrl.wen   )
    connect( self.dpath.waddr,    self.ctrl.waddr )
    connect( self.dpath.raddr,    self.ctrl.raddr )

  #-----------------------------------------------------------------------
  # Line tracing
  #-----------------------------------------------------------------------

  def line_trace( self ):

    in_str = \
      pmlib.valrdy.valrdy_to_str( self.enq_bits.value,
        self.enq_val.value, self.enq_rdy.value )

    out_str = \
      pmlib.valrdy.valrdy_to_str( self.deq_bits.value,
        self.deq_val.value, self.deq_rdy.value )

    return "{} () {}"\
      .format( in_str, out_str )


#-------------------------------------------------------------------------------
# Normal Queue Datapath
#-------------------------------------------------------------------------------

class NormalQueueDpath (Model):

  @capture_args
  def __init__( self, nbits ):

    # Interface Ports

    self.enq_bits  = InPort ( nbits )
    self.deq_bits  = OutPort( nbits )

    # Control signal (ctrl -> dpath)

    self.wen       = InPort ( 1 )

    addr_nbits     = int( ceil( log( 8, 2 ) ))

    self.waddr     = InPort( addr_nbits )
    self.raddr     = InPort( addr_nbits )

    # Queue storage

    self.queue = RegisterFile( nbits )

    # Connect queue storage

    connect( self.queue.rd_addr,    self.raddr    )
    connect( self.queue.rd_data,    self.deq_bits )
    connect( self.queue.wr_en,      self.wen      )
    connect( self.queue.wr_addr,    self.waddr    )
    connect( self.queue.wr_data,    self.enq_bits )

#-------------------------------------------------------------------------------
# Normal Queue Control
#-------------------------------------------------------------------------------

class NormalQueueCtrl (Model):

  @capture_args
  def __init__( self, nbits ):

    self.size = 8

    # Interface Ports

    self.enq_val  = InPort ( 1 )
    self.enq_rdy  = OutPort( 1 )
    self.deq_val  = OutPort( 1 )
    self.deq_rdy  = InPort ( 1 )

    # Control signal (ctrl -> dpath)

    self.wen      = OutPort( 1 )

    addr_nbits    = int( ceil( log( 8, 2 ) ))

    self.waddr    = OutPort( addr_nbits )
    self.raddr    = OutPort( addr_nbits )

    # Wires

    self.full         = Wire( 1 )
    self.empty        = Wire( 1 )

    self.do_enq       = Wire( 1 )
    self.do_deq       = Wire( 1 )

    self.enq_ptr      = Wire( addr_nbits )
    self.deq_ptr      = Wire( addr_nbits )

    self.enq_ptr_next = Wire( addr_nbits )
    self.deq_ptr_next = Wire( addr_nbits )


  @combinational
  def comb( self ):

    # only enqueue/dequeue if valid and ready

    self.do_enq.value = self.enq_rdy.value and self.enq_val.value
    self.do_deq.value = self.deq_rdy.value and self.deq_val.value

    # enq ptr incrementer

    if self.enq_ptr.value == (self.size - 1):
      enq_ptr_inc = 0
    else:
      enq_ptr_inc = self.enq_ptr.value + 1

    # deq ptr incrementer

    if self.deq_ptr.value == (self.size - 1):
      deq_ptr_inc = 0
    else:
      deq_ptr_inc = self.deq_ptr.value + 1

    # set the next ptr value

    if self.do_enq.value:
      self.enq_ptr_next.value = enq_ptr_inc
    else:
      self.enq_ptr_next.value = self.enq_ptr.value

    if self.do_deq.value:
      self.deq_ptr_next.value = deq_ptr_inc
    else:
      self.deq_ptr_next.value = self.deq_ptr.value

    # stuff

    self.empty.value = (not self.full.value and
                       (self.enq_ptr.value == self.deq_ptr.value))

    # set output signals

    self.enq_rdy.value = not self.full.value
    # TODO: add check when writing an InPort!
    self.deq_val.value = not self.empty.value
    self.wen.value     = self.do_enq.value
    self.waddr.value   = self.enq_ptr.value
    self.raddr.value   = self.deq_ptr.value

  @posedge_clk
  def seq( self ):

    if self.reset.value:
      self.deq_ptr.next = 0
      self.enq_ptr.next = 0
    else:
      self.deq_ptr.next = self.deq_ptr_next.value
      self.enq_ptr.next = self.enq_ptr_next.value

    if self.reset.value:
      self.full.next    = 0
    elif (self.do_enq.value and not self.do_deq.value and
          (self.enq_ptr_next.value == self.deq_ptr.value)):
      self.full.next    = 1
    elif (self.do_deq.value and self.full.value):
      self.full.next    = 0
    else:
      self.full.next    = self.full.value


