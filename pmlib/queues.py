#=========================================================================
# queues
#=========================================================================
# This file contains a collection of various queue model implementations

from   pymtl import *
import pmlib

from   math import ceil, log

#=========================================================================
# Single-Element Normal Queue
#=========================================================================

#-------------------------------------------------------------------------
# Single-Element Normal Queue Datapath
#-------------------------------------------------------------------------

class SingleElementNormalQueueDpath (Model):

  def __init__( self, data_nbits ):

    # Interface Ports

    self.enq_bits  = InPort  ( data_nbits )
    self.deq_bits  = OutPort ( data_nbits )

    # Control signal (ctrl -> dpath)

    self.wen       = InPort  ( 1     )

    # Queue storage

    self.queue     = pmlib.regs.RegEn( data_nbits )

    # Connect queue storage

    connect( self.queue.en,  self.wen      )
    connect( self.queue.in_, self.enq_bits )
    connect( self.queue.out, self.deq_bits )

#-------------------------------------------------------------------------
# Single-Element Normal Queue Control
#-------------------------------------------------------------------------

class SingleElementNormalQueueCtrl (Model):

  def __init__( self ):

    # Interface Ports

    self.enq_val  = InPort  ( 1 )
    self.enq_rdy  = OutPort ( 1 )
    self.deq_val  = OutPort ( 1 )
    self.deq_rdy  = InPort  ( 1 )

    # Control signal (ctrl -> dpath)

    self.wen      = OutPort ( 1 )

    # Full bit storage

    self.full     = Wire ( 1 )

  @combinational
  def comb( self ):

    # wen control signal: set the write enable signal if the storage queue
    # is empty and a valid enqueue request is present

    self.wen.value       = ~self.full.value & self.enq_val.value

    # enq_rdy signal is asserted when the single element queue storage is
    # empty

    self.enq_rdy.value   = ~self.full.value

    # deq_val signal is asserted when the single element queue storage is
    # full

    self.deq_val.value   = self.full.value

  @posedge_clk
  def seq( self ):

    # full bit calculation: the full bit is cleared when a dequeue
    # transaction occurs, the full bit is set when the queue storage is
    # empty and a enqueue transaction occurs

    if self.reset.value:
      self.full.next = 0
    elif   self.deq_rdy.value and self.deq_val.value:
      self.full.next = 0
    elif self.enq_rdy.value and self.enq_val.value:
      self.full.next = 1
    else:
      self.full.next = self.full.value

#-------------------------------------------------------------------------
# Single-Element Normal Queue
#-------------------------------------------------------------------------

class SingleElementNormalQueue (Model):

  def __init__( self, data_nbits ):

    # Interface Ports

    self.enq_bits = InPort  ( data_nbits )
    self.enq_val  = InPort  ( 1 )
    self.enq_rdy  = OutPort ( 1 )

    self.deq_bits = OutPort ( data_nbits )
    self.deq_val  = OutPort ( 1 )
    self.deq_rdy  = InPort  ( 1 )

    # Ctrl and Dpath unit instantiation

    self.ctrl  = SingleElementNormalQueueCtrl ()
    self.dpath = SingleElementNormalQueueDpath( data_nbits )

    # Ctrl unit connections

    connect( self.ctrl.enq_val, self.enq_val )
    connect( self.ctrl.enq_rdy, self.enq_rdy )
    connect( self.ctrl.deq_val, self.deq_val )
    connect( self.ctrl.deq_rdy, self.deq_rdy )

    # Dpath unit connections

    connect( self.dpath.enq_bits, self.enq_bits )
    connect( self.dpath.deq_bits, self.deq_bits )

    # Control Signal connections (ctrl -> dpath)

    connect( self.dpath.wen,      self.ctrl.wen )

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

#=========================================================================
# Single-Element Bypass Queue
#=========================================================================

#-------------------------------------------------------------------------
# Single-Element Bypass Queue Datapath
#-------------------------------------------------------------------------

class SingleElementBypassQueueDpath (Model):

  def __init__( self, data_nbits ):

    # Interface Ports

    self.enq_bits      = InPort  ( data_nbits )
    self.deq_bits      = OutPort ( data_nbits )

    # Control signal (ctrl -> dpath)

    self.wen            = InPort ( 1 )
    self.bypass_mux_sel = InPort ( 1 )

    # Queue storage

    self.queue = pmlib.regs.RegEn( data_nbits )

    connect( self.queue.en,  self.wen      )
    connect( self.queue.in_, self.enq_bits )

    # Bypass mux

    self.bypass_mux = pmlib.muxes.Mux2( data_nbits )

    connect( self.bypass_mux.in_[0], self.queue.out      )
    connect( self.bypass_mux.in_[1], self.enq_bits       )
    connect( self.bypass_mux.sel,    self.bypass_mux_sel )
    connect( self.bypass_mux.out,    self.deq_bits       )

#-------------------------------------------------------------------------
# Single-Element Bypass Queue Control
#-------------------------------------------------------------------------

class SingleElementBypassQueueCtrl (Model):

  def __init__( self ):

    # Interface Ports

    self.enq_val        = InPort  ( 1 )
    self.enq_rdy        = OutPort ( 1 )
    self.deq_val        = OutPort ( 1 )
    self.deq_rdy        = InPort  ( 1 )

    # Control signal (ctrl -> dpath)

    self.wen            = OutPort ( 1 )
    self.bypass_mux_sel = OutPort ( 1 )

    # Full bit storage

    self.full           = Wire ( 1 )

  @combinational
  def comb( self ):

    # bypass is always enabled when the queue is empty

    self.bypass_mux_sel.value = ~self.full.value

    # wen control signal: set the write enable signal if the storage queue
    # is empty and a valid enqueue request is present

    self.wen.value            = ~self.full.value & self.enq_val.value

    # enq_rdy signal is asserted when the single element queue storage is
    # empty

    self.enq_rdy.value        = ~self.full.value

    # deq_val signal is asserted when the single element queue storage is
    # full or when the queue is empty but we are bypassing

    self.deq_val.value        = self.full.value | ( ~self.full.value &
                                self.enq_val.value )

  @posedge_clk
  def seq( self ):

    # helper signals

    do_deq    = self.deq_rdy.value and self.deq_val.value
    do_enq    = self.enq_rdy.value and self.enq_val.value
    do_bypass = ~self.full.value and do_deq and do_enq

    # full bit calculation: the full bit is cleared when a dequeue
    # transaction occurs; the full bit is set when the queue storage is
    # empty and a enqueue transaction occurs and when we are not bypassing

    if self.reset.value:
      self.full.next = 0
    elif   do_deq:
      self.full.next = 0
    elif   do_enq and not do_bypass:
      self.full.next = 1
    else:
      self.full.next = self.full.value

#-------------------------------------------------------------------------
# Single-Element Bypass Queue
#-------------------------------------------------------------------------

class SingleElementBypassQueue (Model):

  def __init__( self, data_nbits ):

    # Interface Ports

    self.enq_bits = InPort  ( data_nbits )
    self.enq_val  = InPort  ( 1 )
    self.enq_rdy  = OutPort ( 1 )

    self.deq_bits = OutPort ( data_nbits )
    self.deq_val  = OutPort ( 1 )
    self.deq_rdy  = InPort  ( 1 )

    # Ctrl and Dpath unit instantiation

    self.ctrl  = SingleElementBypassQueueCtrl ()
    self.dpath = SingleElementBypassQueueDpath( data_nbits )

    # Ctrl unit connections

    connect( self.ctrl.enq_val, self.enq_val )
    connect( self.ctrl.enq_rdy, self.enq_rdy )
    connect( self.ctrl.deq_val, self.deq_val )
    connect( self.ctrl.deq_rdy, self.deq_rdy )

    # Dpath unit connections

    connect( self.dpath.enq_bits, self.enq_bits )
    connect( self.dpath.deq_bits, self.deq_bits )

    # Control Signal connections (ctrl -> dpath)

    connect( self.dpath.wen,            self.ctrl.wen            )
    connect( self.dpath.bypass_mux_sel, self.ctrl.bypass_mux_sel )

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

#=========================================================================
# Multiple Entry Normal Queue
#=========================================================================

#-------------------------------------------------------------------------
# Normal Queue Datapath
#-------------------------------------------------------------------------

class NormalQueueDpath (Model):

  @capture_args
  def __init__( self, num_entries, data_nbits ):

    # Interface Ports

    self.enq_bits  = InPort  ( data_nbits )
    self.deq_bits  = OutPort ( data_nbits )

    # Control signal (ctrl -> dpath)

    self.wen       = InPort  ( 1 )

    addr_nbits     = int( ceil( log( num_entries, 2 ) ) )

    self.waddr     = InPort  ( addr_nbits )
    self.raddr     = InPort  ( addr_nbits )

    # Queue storage

    self.queue = pmlib.RegisterFile( data_nbits, num_entries )

    # Connect queue storage

    connect( self.queue.rd_addr[0], self.raddr    )
    connect( self.queue.rd_data[0], self.deq_bits )
    connect( self.queue.wr_en,      self.wen      )
    connect( self.queue.wr_addr,    self.waddr    )
    connect( self.queue.wr_data,    self.enq_bits )

#-------------------------------------------------------------------------
# Normal Queue Control
#-------------------------------------------------------------------------

class NormalQueueCtrl (Model):

  @capture_args
  def __init__( self, num_entries ):

    self.num_entries      = num_entries
    addr_nbits            = int( ceil( log( num_entries, 2 ) ) )

    # Interface Ports

    self.enq_val          = InPort  ( 1 )
    self.enq_rdy          = OutPort ( 1 )
    self.deq_val          = OutPort ( 1 )
    self.deq_rdy          = InPort  ( 1 )
    self.num_free_entries = OutPort ( addr_nbits + 1 )

    # Control signal (ctrl -> dpath)

    self.wen              = OutPort ( 1 )
    self.waddr            = OutPort ( addr_nbits )
    self.raddr            = OutPort ( addr_nbits )

    # Wires

    self.full             = Wire ( 1 )
    self.empty            = Wire ( 1 )
    self.do_enq           = Wire ( 1 )
    self.do_deq           = Wire ( 1 )
    self.enq_ptr          = Wire ( addr_nbits )
    self.deq_ptr          = Wire ( addr_nbits )
    self.enq_ptr_next     = Wire ( addr_nbits )
    self.deq_ptr_next     = Wire ( addr_nbits )

  @combinational
  def comb( self ):

    # only enqueue/dequeue if valid and ready

    self.do_enq.value = self.enq_rdy.value and self.enq_val.value
    self.do_deq.value = self.deq_rdy.value and self.deq_val.value

    # enq ptr incrementer

    if self.enq_ptr.value == (self.num_entries - 1):
      enq_ptr_inc = 0
    else:
      enq_ptr_inc = self.enq_ptr.value + 1

    # deq ptr incrementer

    if self.deq_ptr.value == (self.num_entries - 1):
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

    # number of free entries calculation

    if   self.reset.value:
      self.num_free_entries.value = self.num_entries
    elif self.full.value:
      self.num_free_entries.value = 0
    elif self.empty.value:
      self.num_free_entries.value = self.num_entries
    elif self.enq_ptr.value > self.deq_ptr.value:
      self.num_free_entries.value = \
        self.num_entries - ( self.enq_ptr.value.uint - self.deq_ptr.value.uint )
    elif self.deq_ptr.value > self.enq_ptr.value:
      self.num_free_entries.value = \
        self.deq_ptr.value.uint - self.enq_ptr.value.uint

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

#-------------------------------------------------------------------------------
# Single-Element Normal Queue
#-------------------------------------------------------------------------------

class NormalQueue ( Model ):

  @capture_args
  def __init__( self, num_entries, data_nbits ):

    # TODO: add check to prevent instantiation of single element queue

    self.num_entries      = num_entries
    addr_nbits            = int( ceil( log( num_entries, 2 ) ) )

    # Interface Ports

    self.enq_bits         = InPort  ( data_nbits )
    self.enq_val          = InPort  ( 1 )
    self.enq_rdy          = OutPort ( 1 )

    self.deq_bits         = OutPort ( data_nbits )
    self.deq_val          = OutPort ( 1 )
    self.deq_rdy          = InPort  ( 1 )

    self.num_free_entries = OutPort ( addr_nbits + 1 )

    # Ctrl and Dpath unit instantiation

    self.ctrl  = NormalQueueCtrl ( num_entries             )
    self.dpath = NormalQueueDpath( num_entries, data_nbits )

    # Ctrl unit connections

    connect( self.ctrl.enq_val,          self.enq_val          )
    connect( self.ctrl.enq_rdy,          self.enq_rdy          )
    connect( self.ctrl.deq_val,          self.deq_val          )
    connect( self.ctrl.deq_rdy,          self.deq_rdy          )
    connect( self.ctrl.num_free_entries, self.num_free_entries )

    # Dpath unit connections

    connect( self.dpath.enq_bits, self.enq_bits   )
    connect( self.dpath.deq_bits, self.deq_bits   )

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

    return "{} ({}) {}"\
      .format( in_str, self.num_free_entries.value, out_str )

