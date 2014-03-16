#=========================================================================
# queues_rtl_test.py
#=========================================================================
# This file contains a collection of various queue model implementations

from new_pymtl import *
from new_pmlib import *

#=========================================================================
# Single-Element Normal Queue
#=========================================================================
class SingleElementNormalQueue( Model ):

  def __init__( s, data_nbits ):

    s.data_nbits = data_nbits

    # Interface Ports

    s.enq_bits = InPort  ( data_nbits )
    s.enq_val  = InPort  ( 1 )
    s.enq_rdy  = OutPort ( 1 )

    s.deq_bits = OutPort ( data_nbits )
    s.deq_val  = OutPort ( 1 )
    s.deq_rdy  = InPort  ( 1 )

  def elaborate_logic( s ):

    # Ctrl and Dpath unit instantiation

    s.ctrl  = SingleElementNormalQueueCtrl ()
    s.dpath = SingleElementNormalQueueDpath( s.data_nbits )

    # Ctrl unit connections

    s.connect( s.ctrl.enq_val, s.enq_val )
    s.connect( s.ctrl.enq_rdy, s.enq_rdy )
    s.connect( s.ctrl.deq_val, s.deq_val )
    s.connect( s.ctrl.deq_rdy, s.deq_rdy )

    # Dpath unit connections

    s.connect( s.dpath.enq_bits, s.enq_bits )
    s.connect( s.dpath.deq_bits, s.deq_bits )

    # Control Signal connections (ctrl -> dpath)

    s.connect( s.dpath.wen,      s.ctrl.wen )

  #-----------------------------------------------------------------------
  # Line tracing
  #-----------------------------------------------------------------------

  def line_trace( s ):

    in_str = \
      valrdy.valrdy_to_str( s.enq_bits.value,
        s.enq_val.value, s.enq_rdy.value )

    out_str = \
      valrdy.valrdy_to_str( s.deq_bits.value,
        s.deq_val.value, s.deq_rdy.value )

    return "{} () {}"\
      .format( in_str, out_str )


#-------------------------------------------------------------------------
# Single-Element Normal Queue Datapath
#-------------------------------------------------------------------------
class SingleElementNormalQueueDpath( Model ):

  def __init__( s, data_nbits ):

    s.data_nbits = data_nbits

    # Interface Ports

    s.enq_bits  = InPort  ( data_nbits )
    s.deq_bits  = OutPort ( data_nbits )

    # Control signal (ctrl -> dpath)

    s.wen       = InPort  ( 1     )

  def elaborate_logic( s ):

    # Queue storage

    s.queue = regs.RegEn( s.data_nbits )

    # Connect queue storage

    s.connect( s.queue.en,  s.wen      )
    s.connect( s.queue.in_, s.enq_bits )
    s.connect( s.queue.out, s.deq_bits )

#-------------------------------------------------------------------------
# Single-Element Normal Queue Control
#-------------------------------------------------------------------------
class SingleElementNormalQueueCtrl( Model ):

  def __init__( s ):

    # Interface Ports

    s.enq_val  = InPort  ( 1 )
    s.enq_rdy  = OutPort ( 1 )
    s.deq_val  = OutPort ( 1 )
    s.deq_rdy  = InPort  ( 1 )

    # Control signal (ctrl -> dpath)

    s.wen      = OutPort ( 1 )

  def elaborate_logic( s ):

    s.full     = Wire ( 1 )

    @s.combinational
    def comb():

      # wen control signal: set the write enable signal if the storage queue
      # is empty and a valid enqueue request is present

      s.wen.value       = ~s.full.value & s.enq_val.value

      # enq_rdy signal is asserted when the single element queue storage is
      # empty

      s.enq_rdy.value   = ~s.full.value

      # deq_val signal is asserted when the single element queue storage is
      # full

      s.deq_val.value   = s.full.value

    @s.posedge_clk
    def seq():

      # full bit calculation: the full bit is cleared when a dequeue
      # transaction occurs, the full bit is set when the queue storage is
      # empty and a enqueue transaction occurs

      if s.reset.value:
        s.full.next = 0
      elif   s.deq_rdy.value and s.deq_val.value:
        s.full.next = 0
      elif s.enq_rdy.value and s.enq_val.value:
        s.full.next = 1
      else:
        s.full.next = s.full.value

#=========================================================================
# Single-Element Bypass Queue
#=========================================================================
class SingleElementBypassQueue( Model ):

  def __init__( s, data_nbits ):

    s.data_nbits = data_nbits

    # Interface Ports

    s.enq_bits = InPort  ( data_nbits )
    s.enq_val  = InPort  ( 1 )
    s.enq_rdy  = OutPort ( 1 )

    s.deq_bits = OutPort ( data_nbits )
    s.deq_val  = OutPort ( 1 )
    s.deq_rdy  = InPort  ( 1 )

  def elaborate_logic( s ):

    # Ctrl and Dpath unit instantiation

    s.ctrl  = SingleElementBypassQueueCtrl ()
    s.dpath = SingleElementBypassQueueDpath( s.data_nbits )

    # Ctrl unit connections

    s.connect( s.ctrl.enq_val, s.enq_val )
    s.connect( s.ctrl.enq_rdy, s.enq_rdy )
    s.connect( s.ctrl.deq_val, s.deq_val )
    s.connect( s.ctrl.deq_rdy, s.deq_rdy )

    # Dpath unit connections

    s.connect( s.dpath.enq_bits, s.enq_bits )
    s.connect( s.dpath.deq_bits, s.deq_bits )

    # Control Signal connections (ctrl -> dpath)

    s.connect( s.dpath.wen,            s.ctrl.wen            )
    s.connect( s.dpath.bypass_mux_sel, s.ctrl.bypass_mux_sel )

  #-----------------------------------------------------------------------
  # Line tracing
  #-----------------------------------------------------------------------

  def line_trace( s ):

    in_str = \
      valrdy.valrdy_to_str( s.enq_bits.value,
        s.enq_val.value, s.enq_rdy.value )

    out_str = \
      valrdy.valrdy_to_str( s.deq_bits.value,
        s.deq_val.value, s.deq_rdy.value )

    return "{} () {}"\
      .format( in_str, out_str )


#-------------------------------------------------------------------------
# Single-Element Bypass Queue Datapath
#-------------------------------------------------------------------------
class SingleElementBypassQueueDpath( Model ):

  def __init__( s, data_nbits ):

    s.data_nbits = data_nbits

    # Interface Ports

    s.enq_bits      = InPort  ( data_nbits )
    s.deq_bits      = OutPort ( data_nbits )

    # Control signal (ctrl -> dpath)

    s.wen            = InPort ( 1 )
    s.bypass_mux_sel = InPort ( 1 )

  def elaborate_logic( s ):

    # Queue storage

    s.queue = regs.RegEn( s.data_nbits )

    s.connect( s.queue.en,  s.wen      )
    s.connect( s.queue.in_, s.enq_bits )

    # Bypass mux

    s.bypass_mux = Mux( s.data_nbits, 2 )

    s.connect( s.bypass_mux.in_[0], s.queue.out      )
    s.connect( s.bypass_mux.in_[1], s.enq_bits       )
    s.connect( s.bypass_mux.sel,    s.bypass_mux_sel )
    s.connect( s.bypass_mux.out,    s.deq_bits       )

#-------------------------------------------------------------------------
# Single-Element Bypass Queue Control
#-------------------------------------------------------------------------
class SingleElementBypassQueueCtrl( Model ):

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

      s.bypass_mux_sel.value = ~s.full.value

      # wen control signal: set the write enable signal if the storage queue
      # is empty and a valid enqueue request is present

      s.wen.value            = ~s.full.value & s.enq_val.value

      # enq_rdy signal is asserted when the single element queue storage is
      # empty

      s.enq_rdy.value        = ~s.full.value

      # deq_val signal is asserted when the single element queue storage is
      # full or when the queue is empty but we are bypassing

      s.deq_val.value        = s.full.value | ( ~s.full.value &
                                  s.enq_val.value )

      # TODO: figure out how to make these work as temporaries
      # helper signals

      s.do_deq.value    = s.deq_rdy.value and s.deq_val.value
      s.do_enq.value    = s.enq_rdy.value and s.enq_val.value
      s.do_bypass.value = (~s.full.value and s.do_deq.value
                              and s.do_enq.value)

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
      elif   s.do_deq.value:
        s.full.next = 0
      #elif   do_enq and not do_bypass:
      elif   s.do_enq.value and not s.do_bypass.value:
        s.full.next = 1
      else:
        s.full.next = s.full.value

#=========================================================================
# Multiple Entry Normal Queue
#=========================================================================
class NormalQueue( Model ):

  def __init__( s, num_entries, data_nbits ):

    s.num_entries = num_entries
    s.data_nbits  = data_nbits
    s.addr_nbits  = get_sel_nbits( num_entries )

    # Interface Ports

    s.enq_bits         = InPort  ( data_nbits )
    s.enq_val          = InPort  ( 1 )
    s.enq_rdy          = OutPort ( 1 )

    s.deq_bits         = OutPort ( data_nbits )
    s.deq_val          = OutPort ( 1 )
    s.deq_rdy          = InPort  ( 1 )

    s.num_free_entries = OutPort ( s.addr_nbits + 1 )

  def elaborate_logic( s ):

    # Ctrl and Dpath unit instantiation

    s.ctrl  = NormalQueueCtrl ( s.num_entries               )
    s.dpath = NormalQueueDpath( s.num_entries, s.data_nbits )

    # Ctrl unit connections

    s.connect( s.ctrl.enq_val,          s.enq_val          )
    s.connect( s.ctrl.enq_rdy,          s.enq_rdy          )
    s.connect( s.ctrl.deq_val,          s.deq_val          )
    s.connect( s.ctrl.deq_rdy,          s.deq_rdy          )
    s.connect( s.ctrl.num_free_entries, s.num_free_entries )

    # Dpath unit connections

    s.connect( s.dpath.enq_bits, s.enq_bits   )
    s.connect( s.dpath.deq_bits, s.deq_bits   )

    # Control Signal connections (ctrl -> dpath)

    s.connect( s.dpath.wen,      s.ctrl.wen   )
    s.connect( s.dpath.waddr,    s.ctrl.waddr )
    s.connect( s.dpath.raddr,    s.ctrl.raddr )

  #-----------------------------------------------------------------------
  # Line tracing
  #-----------------------------------------------------------------------

  def line_trace( s ):

    in_str = \
      valrdy.valrdy_to_str( s.enq_bits.value,
        s.enq_val.value, s.enq_rdy.value )

    out_str = \
      valrdy.valrdy_to_str( s.deq_bits.value,
        s.deq_val.value, s.deq_rdy.value )

    return "{} ({}) {}"\
      .format( in_str, s.num_free_entries.value, out_str )

#-------------------------------------------------------------------------
# Normal Queue Datapath
#-------------------------------------------------------------------------
class NormalQueueDpath( Model ):

  def __init__( s, num_entries, data_nbits ):

    s.num_entries = num_entries
    s.data_nbits  = data_nbits
    s.addr_nbits  = get_sel_nbits( num_entries )

    # Interface Ports

    s.enq_bits  = InPort  ( data_nbits )
    s.deq_bits  = OutPort ( data_nbits )

    # Control signal (ctrl -> dpath)

    s.wen       = InPort  ( 1 )

    s.waddr     = InPort  ( s.addr_nbits )
    s.raddr     = InPort  ( s.addr_nbits )

  def elaborate_logic( s ):

    # Queue storage

    s.queue = RegisterFile( s.data_nbits, s.num_entries )

    # Connect queue storage

    s.connect( s.queue.rd_addr[0], s.raddr    )
    s.connect( s.queue.rd_data[0], s.deq_bits )
    s.connect( s.queue.wr_en,      s.wen      )
    s.connect( s.queue.wr_addr,    s.waddr    )
    s.connect( s.queue.wr_data,    s.enq_bits )

#-------------------------------------------------------------------------
# Normal Queue Control
#-------------------------------------------------------------------------
class NormalQueueCtrl( Model ):

  def __init__( s, num_entries ):

    s.num_entries  = num_entries
    s.addr_nbits   = get_sel_nbits( num_entries )

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

      # set output signals

      s.empty.value  = (not s.full.value and
                          (s.enq_ptr.value == s.deq_ptr.value))

      s.enq_rdy.value = not s.full.value
      s.deq_val.value = not s.empty.value

      # only enqueue/dequeue if valid and ready

      s.do_enq.value = s.enq_rdy.value and s.enq_val.value
      s.do_deq.value = s.deq_rdy.value and s.deq_val.value

      # set control signals

      s.wen.value     = s.do_enq.value
      s.waddr.value   = s.enq_ptr.value
      s.raddr.value   = s.deq_ptr.value

      # enq ptr incrementer

      if s.enq_ptr.value == (s.num_entries - 1):
        s.enq_ptr_inc.value = 0
      else:
        s.enq_ptr_inc.value = s.enq_ptr.value + 1

      # deq ptr incrementer

      if s.deq_ptr.value == (s.num_entries - 1):
        s.deq_ptr_inc.value = 0
      else:
        s.deq_ptr_inc.value = s.deq_ptr.value + 1

      # set the next ptr value

      if s.do_enq.value:
        s.enq_ptr_next.value = s.enq_ptr_inc.value
      else:
        s.enq_ptr_next.value = s.enq_ptr.value

      if s.do_deq.value:
        s.deq_ptr_next.value = s.deq_ptr_inc.value
      else:
        s.deq_ptr_next.value = s.deq_ptr.value

      # number of free entries calculation

      if   s.reset.value:
        s.num_free_entries.value = s.num_entries
      elif s.full.value:
        s.num_free_entries.value = 0
      elif s.empty.value:
        s.num_free_entries.value = s.num_entries
      elif s.enq_ptr.value > s.deq_ptr.value:
        s.num_free_entries.value = \
          s.num_entries - ( s.enq_ptr - s.deq_ptr )
      elif s.deq_ptr.value > s.enq_ptr.value:
        s.num_free_entries.value = \
          s.deq_ptr - s.enq_ptr

    @s.posedge_clk
    def seq():

      if s.reset.value:
        s.deq_ptr.next = 0
        s.enq_ptr.next = 0
      else:
        s.deq_ptr.next = s.deq_ptr_next.value
        s.enq_ptr.next = s.enq_ptr_next.value

      if s.reset.value:
        s.full.next    = 0
      elif (s.do_enq.value and not s.do_deq.value and
            (s.enq_ptr_next.value == s.deq_ptr.value)):
        s.full.next    = 1
      elif (s.do_deq.value and s.full.value):
        s.full.next    = 0
      else:
        s.full.next    = s.full.value


#=========================================================================
# Single-Element Pipelined Queue
#=========================================================================
class SingleElementPipelinedQueue( Model ):

  def __init__( s, data_nbits ):

    s.data_nbits = data_nbits

    # Interface Ports

    s.enq_bits = InPort  ( data_nbits )
    s.enq_val  = InPort  ( 1 )
    s.enq_rdy  = OutPort ( 1 )

    s.deq_bits = OutPort ( data_nbits )
    s.deq_val  = OutPort ( 1 )
    s.deq_rdy  = InPort  ( 1 )

  def elaborate_logic( s ):

    # Ctrl and Dpath unit instantiation

    s.ctrl  = SingleElementPipelinedQueueCtrl ()
    s.dpath = SingleElementPipelinedQueueDpath( s.data_nbits )

    # Ctrl unit connections

    s.connect( s.ctrl.enq_val, s.enq_val )
    s.connect( s.ctrl.enq_rdy, s.enq_rdy )
    s.connect( s.ctrl.deq_val, s.deq_val )
    s.connect( s.ctrl.deq_rdy, s.deq_rdy )

    # Dpath unit connections

    s.connect( s.dpath.enq_bits, s.enq_bits )
    s.connect( s.dpath.deq_bits, s.deq_bits )

    # Control Signal connections (ctrl -> dpath)

    s.connect( s.dpath.wen,      s.ctrl.wen )

  #-----------------------------------------------------------------------
  # Line tracing
  #-----------------------------------------------------------------------

  def line_trace( s ):

    in_str = \
      valrdy.valrdy_to_str( s.enq_bits.value,
        s.enq_val.value, s.enq_rdy.value )

    out_str = \
      valrdy.valrdy_to_str( s.deq_bits.value,
        s.deq_val.value, s.deq_rdy.value )

    return "{} () {}"\
      .format( in_str, out_str )

#-------------------------------------------------------------------------
# Single-Element Pipelined Queue Datapath
#-------------------------------------------------------------------------
class SingleElementPipelinedQueueDpath( Model ):

  def __init__( s, data_nbits ):

    s.data_nbits = data_nbits

    # Interface Ports

    s.enq_bits  = InPort  ( data_nbits )
    s.deq_bits  = OutPort ( data_nbits )

    # Control signal (ctrl -> dpath)

    s.wen       = InPort  ( 1     )

  def elaborate_logic( s ):

    # Queue storage

    s.queue = regs.RegEn( s.data_nbits )

    # Connect queue storage

    s.connect( s.queue.en,  s.wen      )
    s.connect( s.queue.in_, s.enq_bits )
    s.connect( s.queue.out, s.deq_bits )

#-------------------------------------------------------------------------
# Single-Element Pipelined Queue Control
#-------------------------------------------------------------------------
class SingleElementPipelinedQueueCtrl( Model ):

  def __init__( s ):

    # Interface Ports

    s.enq_val = InPort  ( 1 )
    s.enq_rdy = OutPort ( 1 )
    s.deq_val = OutPort ( 1 )
    s.deq_rdy = InPort  ( 1 )

    # Control signal (ctrl -> dpath)

    s.wen     = OutPort ( 1 )

  def elaborate_logic( s ):

    # Full bit storage

    s.full    = Wire ( 1 )

    # Temporary Wires

    s.do_enq  = Wire( 1 )
    s.do_deq  = Wire( 1 )
    s.do_pipe = Wire( 1 )

    @s.combinational
    def comb():

      # enq_rdy signal is asserted when the single element queue storage is
      # empty

      s.enq_rdy.value        = ~s.full.value | ( s.full.value &
                                  s.deq_rdy.value )

      # deq_val signal is asserted when the single element queue storage is
      # full or when the queue is empty but we are bypassing

      s.deq_val.value        = s.full.value

      # wen control signal: set the write enable signal if the storage queue
      # is empty and a valid enqueue request is present

      s.wen.value            = ( ~s.full.value | ( s.full.value &
                                    s.deq_rdy.value ) ) & s.enq_val.value

      # helper signals

      s.do_deq.value  = s.deq_rdy.value & s.deq_val.value
      s.do_enq.value  = s.enq_rdy.value & s.enq_val.value
      s.do_pipe.value = s.full.value & s.do_deq.value & s.do_enq.value

    @s.posedge_clk
    def seq():

      # full bit calculation: the full bit is cleared when a dequeue
      # transaction occurs; the full bit is set when the queue storage is
      # empty and a enqueue transaction occurs and when we are not bypassing

      if s.reset.value:
        s.full.next = 0
      elif   s.do_deq.value & ~s.do_pipe.value:
        s.full.next = 0
      elif   s.do_enq.value:
        s.full.next = 1
      else:
        s.full.next = s.full.value

