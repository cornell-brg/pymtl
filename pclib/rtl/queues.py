#=======================================================================
# queues.py
#=======================================================================
'''A collection of queue model implementations.'''

from pymtl      import *
from pclib.ifcs import InValRdyBundle, OutValRdyBundle
from pclib.rtl  import RegEn, Mux, RegisterFile

#-----------------------------------------------------------------------
# SingleElementNormalQueue
#-----------------------------------------------------------------------
class SingleElementNormalQueue( Model ):

  def __init__( s, dtype ):

    s.enq = InValRdyBundle ( dtype )
    s.deq = OutValRdyBundle( dtype )

    # Ctrl and Dpath unit instantiation

    s.ctrl  = SingleElementNormalQueueCtrl ()
    s.dpath = SingleElementNormalQueueDpath( dtype )

    # Ctrl unit connections

    s.connect( s.ctrl.enq_val, s.enq.val )
    s.connect( s.ctrl.enq_rdy, s.enq.rdy )
    s.connect( s.ctrl.deq_val, s.deq.val )
    s.connect( s.ctrl.deq_rdy, s.deq.rdy )

    # Dpath unit connections

    s.connect( s.dpath.enq_bits, s.enq.msg )
    s.connect( s.dpath.deq_bits, s.deq.msg )

    # Control Signal connections (ctrl -> dpath)

    s.connect( s.dpath.wen, s.ctrl.wen )

  def line_trace( s ):
    return "{} () {}".format( s.enq, s.deq )

#-----------------------------------------------------------------------
# SingleElementNormalQueueDpath
#-----------------------------------------------------------------------
class SingleElementNormalQueueDpath( Model ):

  def __init__( s, dtype ):

    s.enq_bits  = InPort  ( dtype )
    s.deq_bits  = OutPort ( dtype )

    # Control signal (ctrl -> dpath)
    s.wen       = InPort  ( 1     )

    # Queue storage

    s.queue = RegEn( dtype )

    # Connect queue storage

    s.connect( s.queue.en,  s.wen      )
    s.connect( s.queue.in_, s.enq_bits )
    s.connect( s.queue.out, s.deq_bits )

#-----------------------------------------------------------------------
# SingleElementNormalQueueCtrl
#-----------------------------------------------------------------------
class SingleElementNormalQueueCtrl( Model ):

  def __init__( s ):

    # Interface Ports

    s.enq_val  = InPort  ( 1 )
    s.enq_rdy  = OutPort ( 1 )
    s.deq_val  = OutPort ( 1 )
    s.deq_rdy  = InPort  ( 1 )

    # Control signal (ctrl -> dpath)
    s.wen      = OutPort ( 1 )

    s.full     = Wire ( 1 )

    @s.combinational
    def comb():

      # wen control signal: set the write enable signal if the storage queue
      # is empty and a valid enqueue request is present

      s.wen.value = ~s.full & s.enq_val

      # enq_rdy signal is asserted when the single element queue storage is
      # empty

      s.enq_rdy.value = ~s.full

      # deq_val signal is asserted when the single element queue storage is
      # full

      s.deq_val.value = s.full

    @s.posedge_clk
    def seq():

      # full bit calculation: the full bit is cleared when a dequeue
      # transaction occurs, the full bit is set when the queue storage is
      # empty and a enqueue transaction occurs

      if   s.reset:                 s.full.next = 0
      elif s.deq_rdy and s.deq_val: s.full.next = 0
      elif s.enq_rdy and s.enq_val: s.full.next = 1
      else:                         s.full.next = s.full

#-----------------------------------------------------------------------
# SingleElementBypassQueue
#-----------------------------------------------------------------------
class SingleElementBypassQueue( Model ):

  def __init__( s, dtype ):

    s.enq = InValRdyBundle ( dtype )
    s.deq = OutValRdyBundle( dtype )

    # Ctrl and Dpath unit instantiation

    s.ctrl  = SingleElementBypassQueueCtrl ()
    s.dpath = SingleElementBypassQueueDpath( dtype )

    # Ctrl unit connections

    s.connect( s.ctrl.enq_val, s.enq.val )
    s.connect( s.ctrl.enq_rdy, s.enq.rdy )
    s.connect( s.ctrl.deq_val, s.deq.val )
    s.connect( s.ctrl.deq_rdy, s.deq.rdy )

    # Dpath unit connections

    s.connect( s.dpath.enq_bits, s.enq.msg )
    s.connect( s.dpath.deq_bits, s.deq.msg )

    # Control Signal connections (ctrl -> dpath)

    s.connect( s.dpath.wen,            s.ctrl.wen            )
    s.connect( s.dpath.bypass_mux_sel, s.ctrl.bypass_mux_sel )

  def line_trace( s ):
    return "{} (v{},r{}) {}".format( s.enq, s.deq.val, s.deq.rdy, s.deq )

#-----------------------------------------------------------------------
# SingleElementBypassQueueDpath
#-----------------------------------------------------------------------
class SingleElementBypassQueueDpath( Model ):

  def __init__( s, dtype ):

    s.enq_bits       = InPort  ( dtype )
    s.deq_bits       = OutPort ( dtype )

    # Control signal (ctrl -> dpath)
    s.wen            = InPort ( 1 )
    s.bypass_mux_sel = InPort ( 1 )

    # Queue storage

    s.queue = RegEn( dtype )

    s.connect( s.queue.en,  s.wen      )
    s.connect( s.queue.in_, s.enq_bits )

    # Bypass mux

    s.bypass_mux = Mux( dtype, 2 )

    s.connect( s.bypass_mux.in_[0], s.queue.out      )
    s.connect( s.bypass_mux.in_[1], s.enq_bits       )
    s.connect( s.bypass_mux.sel,    s.bypass_mux_sel )
    s.connect( s.bypass_mux.out,    s.deq_bits       )

#-----------------------------------------------------------------------
# SingleElementBypassQueueCtrl
#-----------------------------------------------------------------------
class SingleElementBypassQueueCtrl( Model ):

  def __init__( s ):

    s.enq_val        = InPort  ( 1 )
    s.enq_rdy        = OutPort ( 1 )
    s.deq_val        = OutPort ( 1 )
    s.deq_rdy        = InPort  ( 1 )

    # Control signal (ctrl -> dpath)
    s.wen            = OutPort ( 1 )
    s.bypass_mux_sel = OutPort ( 1 )

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

      s.wen.value = ~s.full & s.enq_val

      # enq_rdy signal is asserted when the single element queue storage is
      # empty

      s.enq_rdy.value = ~s.full

      # deq_val signal is asserted when the single element queue storage is
      # full or when the queue is empty but we are bypassing

      s.deq_val.value = s.full | ( ~s.full & s.enq_val )

      # TODO: figure out how to make these work as temporaries
      # helper signals

      s.do_deq.value    = s.deq_rdy and s.deq_val
      s.do_enq.value    = s.enq_rdy and s.enq_val
      s.do_bypass.value = ~s.full and s.do_deq and s.do_enq

    @s.posedge_clk
    def seq():

      # TODO: can't use temporaries here, verilog simulation semantics
      #       don't match the Python semantics!
      ## helper signals

      #do_deq    = s.deq_rdy and s.deq_val
      #do_enq    = s.enq_rdy and s.enq_val
      #do_bypass = ~s.full and do_deq and do_enq

      # full bit calculation: the full bit is cleared when a dequeue
      # transaction occurs; the full bit is set when the queue storage is
      # empty and a enqueue transaction occurs and when we are not bypassing

      if   s.reset:                      s.full.next = 0
      elif s.do_deq:                     s.full.next = 0
      elif s.do_enq and not s.do_bypass: s.full.next = 1
      else:                              s.full.next = s.full

#-----------------------------------------------------------------------
# NormalQueue
#-----------------------------------------------------------------------
class NormalQueue( Model ):

  def __init__( s, num_entries, dtype ):

    s.enq              = InValRdyBundle ( dtype )
    s.deq              = OutValRdyBundle( dtype )
    s.num_free_entries = OutPort( get_nbits(num_entries) )

    # Ctrl and Dpath unit instantiation

    s.ctrl  = NormalQueueCtrl ( num_entries             )
    s.dpath = NormalQueueDpath( num_entries, dtype )

    # Ctrl unit connections

    s.connect( s.ctrl.enq_val,          s.enq.val          )
    s.connect( s.ctrl.enq_rdy,          s.enq.rdy          )
    s.connect( s.ctrl.deq_val,          s.deq.val          )
    s.connect( s.ctrl.deq_rdy,          s.deq.rdy          )
    s.connect( s.ctrl.num_free_entries, s.num_free_entries )

    # Dpath unit connections

    s.connect( s.dpath.enq_bits, s.enq.msg    )
    s.connect( s.dpath.deq_bits, s.deq.msg    )

    # Control Signal connections (ctrl -> dpath)

    s.connect( s.dpath.wen,      s.ctrl.wen   )
    s.connect( s.dpath.waddr,    s.ctrl.waddr )
    s.connect( s.dpath.raddr,    s.ctrl.raddr )

  def line_trace( s ):
    return "{} () {}".format( s.enq, s.deq )

#-----------------------------------------------------------------------
# NormalQueueDpath
#-----------------------------------------------------------------------
class NormalQueueDpath( Model ):

  def __init__( s, num_entries, dtype ):

    s.enq_bits  = InPort  ( dtype )
    s.deq_bits  = OutPort ( dtype )

    # Control signal (ctrl -> dpath)
    addr_nbits  = clog2( num_entries )
    s.wen       = InPort  ( 1 )
    s.waddr     = InPort  ( addr_nbits )
    s.raddr     = InPort  ( addr_nbits )

    # Queue storage

    s.queue = RegisterFile( dtype, num_entries )

    # Connect queue storage

    s.connect( s.queue.rd_addr[0], s.raddr    )
    s.connect( s.queue.rd_data[0], s.deq_bits )
    s.connect( s.queue.wr_en,      s.wen      )
    s.connect( s.queue.wr_addr,    s.waddr    )
    s.connect( s.queue.wr_data,    s.enq_bits )

#-----------------------------------------------------------------------
# NormalQueueCtrl
#-----------------------------------------------------------------------
class NormalQueueCtrl( Model ):

  def __init__( s, num_entries ):

    s.num_entries = num_entries
    addr_nbits    = clog2( num_entries )

    # Interface Ports

    s.enq_val          = InPort  ( 1 )
    s.enq_rdy          = OutPort ( 1 )
    s.deq_val          = OutPort ( 1 )
    s.deq_rdy          = InPort  ( 1 )
    s.num_free_entries = OutPort ( get_nbits( num_entries ) )

    # Control signal (ctrl -> dpath)
    s.wen              = OutPort ( 1 )
    s.waddr            = OutPort ( addr_nbits )
    s.raddr            = OutPort ( addr_nbits )

    # Wires

    s.full             = Wire ( 1 )
    s.empty            = Wire ( 1 )
    s.do_enq           = Wire ( 1 )
    s.do_deq           = Wire ( 1 )
    s.enq_ptr          = Wire ( addr_nbits )
    s.deq_ptr          = Wire ( addr_nbits )
    s.enq_ptr_next     = Wire ( addr_nbits )
    s.deq_ptr_next     = Wire ( addr_nbits )
    # TODO: can't infer these temporaries due to if statement, fix
    s.enq_ptr_inc      = Wire ( addr_nbits )
    s.deq_ptr_inc      = Wire ( addr_nbits )
    s.full_next_cycle  = Wire ( 1 )

    s.last_idx         = num_entries - 1

    @s.combinational
    def comb():

      # set output signals

      s.empty.value   = not s.full and (s.enq_ptr == s.deq_ptr)

      s.enq_rdy.value = not s.full
      s.deq_val.value = not s.empty

      # only enqueue/dequeue if valid and ready

      s.do_enq.value = s.enq_rdy and s.enq_val
      s.do_deq.value = s.deq_rdy and s.deq_val

      # set control signals

      s.wen.value     = s.do_enq
      s.waddr.value   = s.enq_ptr
      s.raddr.value   = s.deq_ptr

      # enq ptr incrementer

      if s.enq_ptr == s.last_idx: s.enq_ptr_inc.value = 0
      else:                       s.enq_ptr_inc.value = s.enq_ptr + 1

      # deq ptr incrementer

      if s.deq_ptr == s.last_idx: s.deq_ptr_inc.value = 0
      else:                       s.deq_ptr_inc.value = s.deq_ptr + 1

      # set the next ptr value

      if s.do_enq: s.enq_ptr_next.value = s.enq_ptr_inc
      else:        s.enq_ptr_next.value = s.enq_ptr

      if s.do_deq: s.deq_ptr_next.value = s.deq_ptr_inc
      else:        s.deq_ptr_next.value = s.deq_ptr

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

      s.full_next_cycle.value = (s.do_enq and not s.do_deq and
                                (s.enq_ptr_next == s.deq_ptr))

    @s.posedge_clk
    def seq():

      if s.reset: s.deq_ptr.next = 0
      else:       s.deq_ptr.next = s.deq_ptr_next

      if s.reset: s.enq_ptr.next = 0
      else:       s.enq_ptr.next = s.enq_ptr_next

      if   s.reset:               s.full.next = 0
      elif s.full_next_cycle:     s.full.next = 1
      elif (s.do_deq and s.full): s.full.next = 0
      else:                       s.full.next = s.full

#-----------------------------------------------------------------------
# SingleElementPipelinedQueue
#-----------------------------------------------------------------------
class SingleElementPipelinedQueue( Model ):

  def __init__( s, dtype ):

    s.enq = InValRdyBundle ( dtype )
    s.deq = OutValRdyBundle( dtype )

    # Ctrl and Dpath unit instantiation

    s.ctrl  = SingleElementPipelinedQueueCtrl ()
    s.dpath = SingleElementPipelinedQueueDpath( dtype )

    # Ctrl unit connections

    s.connect( s.ctrl.enq_val, s.enq.val )
    s.connect( s.ctrl.enq_rdy, s.enq.rdy )
    s.connect( s.ctrl.deq_val, s.deq.val )
    s.connect( s.ctrl.deq_rdy, s.deq.rdy )

    # Dpath unit connections

    s.connect( s.dpath.enq_bits, s.enq.msg )
    s.connect( s.dpath.deq_bits, s.deq.msg )

    # Control Signal connections (ctrl -> dpath)

    s.connect( s.dpath.wen,      s.ctrl.wen )

  def line_trace( s ):
    return "{} () {}".format( s.enq, s.deq )

#-----------------------------------------------------------------------
# SingleElementPipelinedQueueDpath
#-----------------------------------------------------------------------
class SingleElementPipelinedQueueDpath( Model ):

  def __init__( s, dtype ):

    s.enq_bits  = InPort  ( dtype )
    s.deq_bits  = OutPort ( dtype )

    # Control signal (ctrl -> dpath)
    s.wen       = InPort  ( 1     )

    # Queue storage

    s.queue = RegEn( dtype )

    # Connect queue storage

    s.connect( s.queue.en,  s.wen      )
    s.connect( s.queue.in_, s.enq_bits )
    s.connect( s.queue.out, s.deq_bits )

#-----------------------------------------------------------------------
# SingleElementPipelinedQueueCtrl
#-----------------------------------------------------------------------
class SingleElementPipelinedQueueCtrl( Model ):

  def __init__( s ):

    # Interface Ports

    s.enq_val = InPort  ( 1 )
    s.enq_rdy = OutPort ( 1 )
    s.deq_val = OutPort ( 1 )
    s.deq_rdy = InPort  ( 1 )

    # Control signal (ctrl -> dpath)
    s.wen     = OutPort ( 1 )

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

      s.enq_rdy.value = ~s.full | ( s.full & s.deq_rdy )

      # deq_val signal is asserted when the single element queue storage is
      # full or when the queue is empty but we are bypassing

      s.deq_val.value = s.full

      # wen control signal: set the write enable signal if the storage queue
      # is empty and a valid enqueue request is present

      s.wen.value = ( ~s.full | ( s.full & s.deq_rdy ) ) & s.enq_val

      # helper signals

      s.do_deq.value  = s.deq_rdy & s.deq_val
      s.do_enq.value  = s.enq_rdy & s.enq_val
      s.do_pipe.value = s.full & s.do_deq & s.do_enq

    @s.posedge_clk
    def seq():

      # full bit calculation: the full bit is cleared when a dequeue
      # transaction occurs; the full bit is set when the queue storage is
      # empty and a enqueue transaction occurs and when we are not bypassing

      if   s.reset:               s.full.next = 0
      elif s.do_deq & ~s.do_pipe: s.full.next = 0
      elif s.do_enq:              s.full.next = 1
      else:                       s.full.next = s.full

#-----------------------------------------------------------------------
# SingleElementSkidQueue
#-----------------------------------------------------------------------
class SingleElementSkidQueue( Model ):
  '''Similiar to bypass queue, but saves value even if bypassed.

  Can dequeue and enqueue on the same clock edge.
  '''

  def __init__( s, dtype ):

    s.enq = InValRdyBundle ( dtype )
    s.deq = OutValRdyBundle( dtype )

    # Ctrl and Dpath unit instantiation

    s.ctrl  = SingleElementSkidQueueCtrl ()
    s.dpath = SingleElementSkidQueueDpath( dtype )

    # Ctrl unit connections

    s.connect( s.ctrl.enq_val, s.enq.val )
    s.connect( s.ctrl.enq_rdy, s.enq.rdy )
    s.connect( s.ctrl.deq_val, s.deq.val )
    s.connect( s.ctrl.deq_rdy, s.deq.rdy )

    # Dpath unit connections

    s.connect( s.dpath.enq_bits, s.enq.msg )
    s.connect( s.dpath.deq_bits, s.deq.msg )

    # Control Signal connections (ctrl -> dpath)

    s.connect( s.dpath.wen,            s.ctrl.wen            )
    s.connect( s.dpath.bypass_mux_sel, s.ctrl.bypass_mux_sel )

  def line_trace( s ):
    return "{} ({}, {}) {}".format( s.enq,s.ctrl.do_bypass,s.enq.msg, s.deq )

#-----------------------------------------------------------------------
# SingleElementSkidQueueDpath
#-----------------------------------------------------------------------
class SingleElementSkidQueueDpath( Model ):

  def __init__( s, dtype ):

    s.enq_bits      = InPort  ( dtype )
    s.deq_bits      = OutPort ( dtype )

    # Control signal (ctrl -> dpath)

    s.wen            = InPort ( 1 )
    s.bypass_mux_sel = InPort ( 1 )

    # Queue storage

    s.queue = RegEn( dtype )

    s.connect( s.queue.en,  s.wen      )
    s.connect( s.queue.in_, s.enq_bits )

    # Bypass mux

    s.bypass_mux = Mux( dtype, 2 )

    s.connect( s.bypass_mux.in_[0], s.queue.out      )
    s.connect( s.bypass_mux.in_[1], s.enq_bits       )
    s.connect( s.bypass_mux.sel,    s.bypass_mux_sel )
    s.connect( s.bypass_mux.out,    s.deq_bits       )

#-----------------------------------------------------------------------
# SingleElementSkidQueueCtrl
#-----------------------------------------------------------------------
class SingleElementSkidQueueCtrl( Model ):

  def __init__( s ):

    s.enq_val        = InPort  ( 1 )
    s.enq_rdy        = OutPort ( 1 )
    s.deq_val        = OutPort ( 1 )
    s.deq_rdy        = InPort  ( 1 )

    # Control signal (ctrl -> dpath)
    s.wen            = OutPort ( 1 )
    s.bypass_mux_sel = OutPort ( 1 )

    # Full bit storage

    s.full           = Wire ( 1 )
    # TODO: figure out how to make these work as temporaries
    s.do_deq         = Wire ( 1 )
    s.do_enq         = Wire ( 1 )
    s.do_bypass      = Wire ( 1 )

    @s.combinational
    def comb():

      #Dequeue is valid if the queue has an element or is bypassing
      s.deq_val.value = s.full | ( ~s.full & s.enq_val )

      #Dequeue only if the sink is ready and the deq is valid
      s.do_deq.value    = s.deq_rdy and s.deq_val

      #Queue can take a new element if the queue is empty or if
      #queue is dequeuing
      s.enq_rdy.value   = ~s.full | s.do_deq;
      s.do_enq.value    = s.enq_rdy and s.enq_val
      s.wen.value       = s.do_enq
      s.do_bypass.value = s.do_deq and s.do_enq
      s.bypass_mux_sel.value = s.do_bypass

    @s.posedge_clk
    def seq():

      # TODO: can't use temporaries here, verilog simulation semantics
      #       don't match the Python semantics!
      ## helper signals

      #do_deq    = s.deq_rdy and s.deq_val
      #do_enq    = s.enq_rdy and s.enq_val
      #do_bypass = ~s.full and do_deq and do_enq

      # full bit calculation: the full bit is cleared when a dequeue
      # transaction occurs and a new enque is not happening or when
      # an element is bypassed;
      # the full bit is set when the queue storage is
      # empty and a enqueue transaction occurs or when the queue is full
      # and both a enqueue and dequeue are occuring


      if   s.reset:                      s.full.next = 0
      elif s.do_deq and not s.do_enq:    s.full.next = 0
      elif s.do_enq:                     s.full.next = 1
      else:                              s.full.next = s.full

#-------------------------------------------------------------------------
# TwoElementBypassQueuePRTL.py
#-------------------------------------------------------------------------
# FIXME: This is just cascaded two single-element bypass queues. We definitely
# need a better one.

class TwoElementBypassQueue( Model ):

  def __init__( s, dtype ):

    s.enq = InValRdyBundle ( dtype )
    s.deq = OutValRdyBundle( dtype )

    s.queue0 = SingleElementBypassQueue( dtype )
    s.queue1 = SingleElementBypassQueue( dtype )

    s.connect_pairs( s.enq,        s.queue0.enq,
                     s.queue0.deq, s.queue1.enq,
                     s.queue1.deq, s.deq
    )

  def line_trace( s ):
    return "{} (v{},r{}) {}".format( s.enq, s.deq.val, s.deq.rdy, s.deq )
