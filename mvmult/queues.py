#=========================================================================
# queues
#=========================================================================
# This file contains a collection of various queue model implementations

from   new_pymtl import *
import new_pmlib as pmlib

from   math import ceil, log

#=========================================================================
# Single-Element Normal Queue
#=========================================================================

#-------------------------------------------------------------------------
# Single-Element Normal Queue Datapath
#-------------------------------------------------------------------------

class SingleElementNormalQueueDpath (Model):

  def __init__( s, data_nbits ):

    # Interface Ports

    s.enq_bits  = InPort  ( data_nbits )
    s.deq_bits  = OutPort ( data_nbits )

    # Control signal (ctrl -> dpath)

    s.wen       = InPort  ( 1     )

    s.data_nbits = data_nbits

  def elaborate_logic( s ):

    # Queue storage

    s.queue     = pmlib.regs.RegEn( s.data_nbits )

    # Connect queue storage

    s.connect( s.queue.en,  s.wen      )
    s.connect( s.queue.in_, s.enq_bits )
    s.connect( s.queue.out, s.deq_bits )

#-------------------------------------------------------------------------
# Single-Element Normal Queue Control
#-------------------------------------------------------------------------

class SingleElementNormalQueueCtrl (Model):

  def __init__( s ):

    # Interface Ports

    s.enq_val  = InPort  ( 1 )
    s.enq_rdy  = OutPort ( 1 )
    s.deq_val  = OutPort ( 1 )
    s.deq_rdy  = InPort  ( 1 )

    # Control signal (ctrl -> dpath)

    s.wen      = OutPort ( 1 )

  def elaborate_logic( s ):

    # Full bit storage

    s.full     = Wire ( 1 )

    @s.combinational
    def comb():

      # wen control signal: set the write enable signal if the storage queue
      # is empty and a valid enqueue request is present

      s.wen.value       = ~s.full & s.enq_val

      # enq_rdy signal is asserted when the single element queue storage is
      # empty

      s.enq_rdy.value   = ~s.full

      # deq_val signal is asserted when the single element queue storage is
      # full

      s.deq_val.value   = s.full

    @s.posedge_clk
    def seq():

      # full bit calculation: the full bit is cleared when a dequeue
      # transaction occurs, the full bit is set when the queue storage is
      # empty and a enqueue transaction occurs

      if s.reset:
        s.full.next = 0
      elif   s.deq_rdy and s.deq_val:
        s.full.next = 0
      elif s.enq_rdy and s.enq_val:
        s.full.next = 1
      else:
        s.full.next = s.full

#-------------------------------------------------------------------------
# Single-Element Normal Queue
#-------------------------------------------------------------------------

class SingleElementNormalQueue (Model):

  def __init__( s, data_nbits ):

    # Interface Ports

    s.enq_bits = InPort  ( data_nbits )
    s.enq_val  = InPort  ( 1 )
    s.enq_rdy  = OutPort ( 1 )

    s.deq_bits = OutPort ( data_nbits )
    s.deq_val  = OutPort ( 1 )
    s.deq_rdy  = InPort  ( 1 )

    s.data_nbits = data_nbits

  def elaborate_logic( s ):

    # Ctrl and Dpath unit instantiation

    s.ctrl  = SingleElementNormalQueueCtrl ()
    s.dpath = SingleElementNormalQueueDpath( s.data_nbits )

    # Ctrl unit s.connections

    s.connect( s.ctrl.enq_val, s.enq_val )
    s.connect( s.ctrl.enq_rdy, s.enq_rdy )
    s.connect( s.ctrl.deq_val, s.deq_val )
    s.connect( s.ctrl.deq_rdy, s.deq_rdy )

    # Dpath unit s.connections

    s.connect( s.dpath.enq_bits, s.enq_bits )
    s.connect( s.dpath.deq_bits, s.deq_bits )

    # Control Signal s.connections (ctrl -> dpath)

    s.connect( s.dpath.wen,      s.ctrl.wen )

  #-----------------------------------------------------------------------
  # Line tracing
  #-----------------------------------------------------------------------

  def line_trace( s ):

    in_str = \
      pmlib.valrdy.valrdy_to_str( s.enq_bits,
        s.enq_val, s.enq_rdy )

    out_str = \
      pmlib.valrdy.valrdy_to_str( s.deq_bits,
        s.deq_val, s.deq_rdy )

    return "{} () {}"\
      .format( in_str, out_str )

#=========================================================================
# Single-Element Bypass Queue
#=========================================================================

#-------------------------------------------------------------------------
# Single-Element Bypass Queue Datapath
#-------------------------------------------------------------------------

class SingleElementBypassQueueDpath (Model):

  def __init__( s, data_nbits ):

    # Interface Ports

    s.enq_bits      = InPort  ( data_nbits )
    s.deq_bits      = OutPort ( data_nbits )

    # Control signal (ctrl -> dpath)

    s.wen            = InPort ( 1 )
    s.bypass_mux_sel = InPort ( 1 )

    s.data_nbits = data_nbits

  def elaborate_logic( s ):

    # Queue storage

    s.queue = pmlib.regs.RegEn( s.data_nbits )

    s.connect( s.queue.en,  s.wen      )
    s.connect( s.queue.in_, s.enq_bits )

    # Bypass mux

    s.bypass_mux = pmlib.Mux( s.data_nbits, 2 )

    s.connect( s.bypass_mux.in_[0], s.queue.out      )
    s.connect( s.bypass_mux.in_[1], s.enq_bits       )
    s.connect( s.bypass_mux.sel,    s.bypass_mux_sel )
    s.connect( s.bypass_mux.out,    s.deq_bits       )

#-------------------------------------------------------------------------
# Single-Element Bypass Queue Control
#-------------------------------------------------------------------------

class SingleElementBypassQueueCtrl (Model):

  def __init__( s ):

    # Interface Ports

    s.enq_val        = InPort  ( 1 )
    s.enq_rdy        = OutPort ( 1 )
    s.deq_val        = OutPort ( 1 )
    s.deq_rdy        = InPort  ( 1 )

    # Control signal (ctrl -> dpath)

    s.wen            = OutPort ( 1 )
    s.bypass_mux_sel = OutPort ( 1 )

  def elaborate_logic( s ):

    # Full bit storage

    s.full           = Wire ( 1 )
    # TODO: figure out how to make these work as temporaries
    s.do_deq         = Wire ( 1 )
    s.do_enq         = Wire ( 1 )
    s.do_bypass      = Wire ( 1 )

    @s.combinational
    def comb():

      # bypass is always enabled when the queue is empty

      s.bypass_mux_sel.value = ~s.full

      # wen control signal: set the write enable signal if the storage queue
      # is empty and a valid enqueue request is present

      s.wen.value            = ~s.full & s.enq_val

      # enq_rdy signal is asserted when the single element queue storage is
      # empty

      s.enq_rdy.value        = ~s.full

      # deq_val signal is asserted when the single element queue storage is
      # full or when the queue is empty but we are bypassing

      s.deq_val.value        = s.full | ( ~s.full & s.enq_val )

      # TODO: figure out how to make these work as temporaries
      # helper signals

      s.do_deq.value    = s.deq_rdy and s.deq_val
      s.do_enq.value    = s.enq_rdy and s.enq_val
      s.do_bypass.value = (~s.full and s.do_deq and s.do_enq)

    @s.posedge_clk
    def seq():

      # TODO: can't use temporaries here, verilog simulation semantics
      #       don't match the Python semantics!
      ## helper signals

      #do_deq    = s.deq_rdy.value and s.deq_val.value
      #do_enq    = s.enq_rdy.value and s.enq_val.value
      #do_bypass = ~s.full.value and do_deq and do_enq

      # full bit calculation: the full bit is cleared when a dequeue
      # transaction occurs; the full bit is set when the queue storage is
      # empty and a enqueue transaction occurs and when we are not bypassing

      if s.reset.value:
        s.full.next = 0
      #elif   do_deq:
      elif   s.do_deq:
        s.full.next = 0
      #elif   do_enq and not do_bypass:
      elif   s.do_enq and not s.do_bypass:
        s.full.next = 1
      else:
        s.full.next = s.full

#-------------------------------------------------------------------------
# Single-Element Bypass Queue
#-------------------------------------------------------------------------

class SingleElementBypassQueue (Model):

  def __init__( s, data_nbits ):

    # Interface Ports

    s.enq_bits = InPort  ( data_nbits )
    s.enq_val  = InPort  ( 1 )
    s.enq_rdy  = OutPort ( 1 )

    s.deq_bits = OutPort ( data_nbits )
    s.deq_val  = OutPort ( 1 )
    s.deq_rdy  = InPort  ( 1 )

    s.data_nbits = data_nbits

  def elaborate_logic( s ):

    # Ctrl and Dpath unit instantiation

    s.ctrl  = SingleElementBypassQueueCtrl ()
    s.dpath = SingleElementBypassQueueDpath( s.data_nbits )

    # Ctrl unit s.connections

    s.connect( s.ctrl.enq_val, s.enq_val )
    s.connect( s.ctrl.enq_rdy, s.enq_rdy )
    s.connect( s.ctrl.deq_val, s.deq_val )
    s.connect( s.ctrl.deq_rdy, s.deq_rdy )

    # Dpath unit s.connections

    s.connect( s.dpath.enq_bits, s.enq_bits )
    s.connect( s.dpath.deq_bits, s.deq_bits )

    # Control Signal s.connections (ctrl -> dpath)

    s.connect( s.dpath.wen,            s.ctrl.wen            )
    s.connect( s.dpath.bypass_mux_sel, s.ctrl.bypass_mux_sel )

  #-----------------------------------------------------------------------
  # Line tracing
  #-----------------------------------------------------------------------

  def line_trace( s ):

    in_str = \
      pmlib.valrdy.valrdy_to_str( s.enq_bits,
        s.enq_val, s.enq_rdy )

    out_str = \
      pmlib.valrdy.valrdy_to_str( s.deq_bits,
        s.deq_val, s.deq_rdy )

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
  def __init__( s, num_entries, data_nbits ):

    # Interface Ports

    s.enq_bits  = InPort  ( data_nbits )
    s.deq_bits  = OutPort ( data_nbits )

    # Control signal (ctrl -> dpath)

    s.wen       = InPort  ( 1 )

    addr_nbits  = int( ceil( log( num_entries, 2 ) ) )

    s.waddr     = InPort  ( addr_nbits )
    s.raddr     = InPort  ( addr_nbits )

    s.data_nbits  = data_nbits
    s.num_entries = num_entries

  def elaborate_logic( s ):

    # Queue storage

    s.queue = pmlib.RegisterFile( s.data_nbits, s.num_entries )

    # Connect queue storage

    s.connect( s.queue.rd_addr[0], s.raddr    )
    s.connect( s.queue.rd_data[0], s.deq_bits )
    s.connect( s.queue.wr_en,      s.wen      )
    s.connect( s.queue.wr_addr,    s.waddr    )
    s.connect( s.queue.wr_data,    s.enq_bits )

#-------------------------------------------------------------------------
# Normal Queue Control
#-------------------------------------------------------------------------

class NormalQueueCtrl (Model):

  @capture_args
  def __init__( s, num_entries ):

    s.num_entries      = num_entries
    s.addr_nbits       = int( ceil( log( num_entries, 2 ) ) )

    # Interface Ports

    s.enq_val          = InPort  ( 1 )
    s.enq_rdy          = OutPort ( 1 )
    s.deq_val          = OutPort ( 1 )
    s.deq_rdy          = InPort  ( 1 )
    s.num_free_entries = OutPort ( s.addr_nbits + 1 )

    # Control signal (ctrl -> dpath)

    s.wen              = OutPort ( 1 )
    s.waddr            = OutPort ( s.addr_nbits )
    s.raddr            = OutPort ( s.addr_nbits )

  def elaborate_logic( s ):

    # Wires

    s.full             = Wire ( 1 )
    s.empty            = Wire ( 1 )
    s.do_enq           = Wire ( 1 )
    s.do_deq           = Wire ( 1 )
    s.enq_ptr          = Wire ( s.addr_nbits )
    s.deq_ptr          = Wire ( s.addr_nbits )
    s.enq_ptr_next     = Wire ( s.addr_nbits )
    s.deq_ptr_next     = Wire ( s.addr_nbits )
    # TODO: can't infer these temporaries due to if statement, fix
    s.enq_ptr_inc      = Wire ( s.addr_nbits )
    s.deq_ptr_inc      = Wire ( s.addr_nbits )

    @s.combinational
    def comb():

      # determine if queue is empty

      s.empty.value = (not s.full and (s.enq_ptr == s.deq_ptr))

      # set the enq_rdy and deq_val signals based on queue capacity
      # TODO: previously these were set after s.wen was set.
      #       This was a bug, but worked in the older version of the sim!

      s.enq_rdy.value = not s.full
      s.deq_val.value = not s.empty

      # only enqueue/dequeue if valid and ready

      s.do_enq.value = s.enq_rdy and s.enq_val
      s.do_deq.value = s.deq_rdy and s.deq_val

      # set register file signals: write_en, wr_addr and rd_addr

      s.wen.value     = s.do_enq
      s.waddr.value   = s.enq_ptr
      s.raddr.value   = s.deq_ptr

      # enq ptr incrementer

      if s.enq_ptr == (s.num_entries - 1):
        s.enq_ptr_inc.value = 0
      else:
        s.enq_ptr_inc.value = s.enq_ptr + 1

      # deq ptr incrementer

      if s.deq_ptr == (s.num_entries - 1):
        s.deq_ptr_inc.value = 0
      else:
        s.deq_ptr_inc.value = s.deq_ptr + 1

      # set the next ptr value

      if s.do_enq:
        s.enq_ptr_next.value = s.enq_ptr_inc
      else:
        s.enq_ptr_next.value = s.enq_ptr

      if s.do_deq:
        s.deq_ptr_next.value = s.deq_ptr_inc
      else:
        s.deq_ptr_next.value = s.deq_ptr

      # number of free entries calculation

      if   s.reset:
        s.num_free_entries.value = s.num_entries
      elif s.full:
        s.num_free_entries.value = 0
      elif s.empty:
        s.num_free_entries.value = s.num_entries
      elif s.enq_ptr > s.deq_ptr:
        s.num_free_entries.value = s.num_entries - ( s.enq_ptr - s.deq_ptr )
      elif s.deq_ptr > s.enq_ptr:
        s.num_free_entries.value = s.deq_ptr - s.enq_ptr

    @s.posedge_clk
    def seq():

      if s.reset:
        s.deq_ptr.next = 0
        s.enq_ptr.next = 0
      else:
        s.deq_ptr.next = s.deq_ptr_next
        s.enq_ptr.next = s.enq_ptr_next

      if s.reset:
        s.full.next    = 0
      elif (s.do_enq and not s.do_deq and (s.enq_ptr_next == s.deq_ptr)):
        s.full.next    = 1
      elif (s.do_deq and s.full):
        s.full.next    = 0
      else:
        s.full.next    = s.full

#-------------------------------------------------------------------------------
# Single-Element Normal Queue
#-------------------------------------------------------------------------------

class NormalQueue ( Model ):

  @capture_args
  def __init__( s, num_entries, data_nbits ):

    # TODO: add check to prevent instantiation of single element queue

    s.num_entries      = num_entries
    addr_nbits            = int( ceil( log( num_entries, 2 ) ) )

    # Interface Ports

    s.enq_bits         = InPort  ( data_nbits )
    s.enq_val          = InPort  ( 1 )
    s.enq_rdy          = OutPort ( 1 )

    s.deq_bits         = OutPort ( data_nbits )
    s.deq_val          = OutPort ( 1 )
    s.deq_rdy          = InPort  ( 1 )

    s.num_free_entries = OutPort ( addr_nbits + 1 )

    s.data_nbits  = data_nbits
    s.num_entries = num_entries

  def elaborate_logic( s ):

    # Ctrl and Dpath unit instantiation

    s.ctrl  = NormalQueueCtrl ( s.num_entries               )
    s.dpath = NormalQueueDpath( s.num_entries, s.data_nbits )

    # Ctrl unit s.connections

    s.connect( s.ctrl.enq_val,          s.enq_val          )
    s.connect( s.ctrl.enq_rdy,          s.enq_rdy          )
    s.connect( s.ctrl.deq_val,          s.deq_val          )
    s.connect( s.ctrl.deq_rdy,          s.deq_rdy          )
    s.connect( s.ctrl.num_free_entries, s.num_free_entries )

    # Dpath unit s.connections

    s.connect( s.dpath.enq_bits, s.enq_bits   )
    s.connect( s.dpath.deq_bits, s.deq_bits   )

    # Control Signal s.connections (ctrl -> dpath)

    s.connect( s.dpath.wen,      s.ctrl.wen   )
    s.connect( s.dpath.waddr,    s.ctrl.waddr )
    s.connect( s.dpath.raddr,    s.ctrl.raddr )

  #-----------------------------------------------------------------------
  # Line tracing
  #-----------------------------------------------------------------------

  def line_trace( s ):

    in_str = \
      pmlib.valrdy.valrdy_to_str( s.enq_bits,
        s.enq_val, s.enq_rdy )

    out_str = \
      pmlib.valrdy.valrdy_to_str( s.deq_bits,
        s.deq_val, s.deq_rdy )

    return "{} ({}) {}"\
      .format( in_str, s.num_free_entries, out_str )

#=========================================================================
# Single-Element Pipelined Queue
#=========================================================================

#-------------------------------------------------------------------------
# Single-Element Pipelined Queue Datapath
#-------------------------------------------------------------------------

class SingleElementPipelinedQueueDpath (Model):

  @capture_args
  def __init__( s, data_nbits ):

    # Interface Ports

    s.enq_bits  = InPort  ( data_nbits )
    s.deq_bits  = OutPort ( data_nbits )

    # Control signal (ctrl -> dpath)

    s.wen       = InPort  ( 1     )

    s.data_nbits  = data_nbits

  def elaborate_logic( s ):

    # Queue storage

    s.queue     = pmlib.regs.RegEn( s.data_nbits )

    # Connect queue storage

    s.connect( s.queue.en,  s.wen      )
    s.connect( s.queue.in_, s.enq_bits )
    s.connect( s.queue.out, s.deq_bits )

#-------------------------------------------------------------------------
# Single-Element Pipelined Queue Control
#-------------------------------------------------------------------------

class SingleElementPipelinedQueueCtrl (Model):

  @capture_args
  def __init__( s ):

    # Interface Ports

    s.enq_val        = InPort  ( 1 )
    s.enq_rdy        = OutPort ( 1 )
    s.deq_val        = OutPort ( 1 )
    s.deq_rdy        = InPort  ( 1 )

    # Control signal (ctrl -> dpath)

    s.wen            = OutPort ( 1 )

  def elaborate_logic( s ):

    # Full bit storage

    s.full           = Wire ( 1 )

    # Temporary Wires

    s.do_enq  = Wire( 1 )
    s.do_deq  = Wire( 1 )
    s.do_pipe = Wire( 1 )

    @s.combinational
    def comb():

      # enq_rdy signal is asserted when the single element queue storage is
      # empty

      s.enq_rdy.value = ~s.full | ( s.full & s.deq_rdy )

      # deq_val signal is asserted when the single element queue storage is
      # full or when the queue is empty but we are bypassing

      s.deq_val.value = s.full

      # wen control signal: set the write enable signal if the storage queue
      # is empty and a valid enqueue request is present

      s.wen.value     = ( ~s.full | ( s.full & s.deq_rdy ) ) & s.enq_val

      # helper signals

      s.do_deq.value  = s.deq_rdy & s.deq_val
      s.do_enq.value  = s.enq_rdy & s.enq_val
      s.do_pipe.value = s.full & s.do_deq & s.do_enq

    @s.posedge_clk
    def seq():

      # full bit calculation: the full bit is cleared when a dequeue
      # transaction occurs; the full bit is set when the queue storage is
      # empty and a enqueue transaction occurs and when we are not bypassing

      if s.reset:
        s.full.next = 0
      elif   s.do_deq & ~s.do_pipe:
        s.full.next = 0
      elif   s.do_enq:
        s.full.next = 1
      else:
        s.full.next = s.full

#-------------------------------------------------------------------------
# Single-Element Pipelined Queue
#-------------------------------------------------------------------------

class SingleElementPipelinedQueue (Model):

  @capture_args
  def __init__( s, data_nbits ):

    # Interface Ports

    s.enq_bits = InPort  ( data_nbits )
    s.enq_val  = InPort  ( 1 )
    s.enq_rdy  = OutPort ( 1 )

    s.deq_bits = OutPort ( data_nbits )
    s.deq_val  = OutPort ( 1 )
    s.deq_rdy  = InPort  ( 1 )

    s.data_nbits = data_nbits

  def elaborate_logic( s ):

    # Ctrl and Dpath unit instantiation

    s.ctrl  = SingleElementPipelinedQueueCtrl ()
    s.dpath = SingleElementPipelinedQueueDpath( s.data_nbits )

    # Ctrl unit s.connections

    s.connect( s.ctrl.enq_val, s.enq_val )
    s.connect( s.ctrl.enq_rdy, s.enq_rdy )
    s.connect( s.ctrl.deq_val, s.deq_val )
    s.connect( s.ctrl.deq_rdy, s.deq_rdy )

    # Dpath unit s.connections

    s.connect( s.dpath.enq_bits, s.enq_bits )
    s.connect( s.dpath.deq_bits, s.deq_bits )

    # Control Signal s.connections (ctrl -> dpath)

    s.connect( s.dpath.wen,            s.ctrl.wen            )

  #-----------------------------------------------------------------------
  # Line tracing
  #-----------------------------------------------------------------------

  def line_trace( s ):

    in_str = \
      pmlib.valrdy.valrdy_to_str( s.enq_bits,
        s.enq_val, s.enq_rdy )

    out_str = \
      pmlib.valrdy.valrdy_to_str( s.deq_bits,
        s.deq_val, s.deq_rdy )

    return "{} () {}"\
      .format( in_str, out_str )
