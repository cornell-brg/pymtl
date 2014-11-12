#=========================================================================
# GcdUnit cycle-level model
#=========================================================================

from pymtl        import *
from pclib.ifaces import InValRdyBundle, OutValRdyBundle
from pclib.fl     import Queue
from pclib.cl     import InValRdyQueue, OutValRdyQueue

import fractions

#=========================================================================
# GCD Unit Cycle-Level Model
#=========================================================================
class GcdProcCL( Model ):

  #-----------------------------------------------------------------------
  # Constructor: Define Interface
  #-----------------------------------------------------------------------
  def __init__( s, cpu_ifc_types ):

    s.cpu_ifc_req  = InValRdyBundle  ( cpu_ifc_types.req  )
    s.cpu_ifc_resp = OutValRdyBundle ( cpu_ifc_types.resp )
    
    s.cpu_req_q    = InValRdyQueue   ( cpu_ifc_types.req  )
    s.cpu_resp_q   = OutValRdyQueue  ( cpu_ifc_types.resp )

  def elaborate_logic( s ):
    
    s.connect( s.cpu_req_q.in_ , s.cpu_ifc_req )
    s.connect( s.cpu_resp_q.out, s.cpu_ifc_resp)
    
    s.go      = False
    s.src0    = 0
    s.src1    = 0
    s.result  = 0

    s.counter = 0
    s.counter_done = False

    @s.tick_cl
    def logic():

      s.cpu_req_q.xtick()
      s.cpu_resp_q.xtick()

      if s.go and not s.counter_done:
        while( s.src1 != 0 ):
          # Euclid's algorithm 
          if s.src0 < s.src1:
            tmp    = s.src1
            s.src1 = s.src0
            s.src0 = tmp
          s.src0 = s.src0 - s.src1
          s.counter += 1
        s.counter_done = True
      
      elif not s.cpu_req_q.is_empty() and not s.cpu_resp_q.is_full():
	req = s.cpu_req_q.deq()
	if req.ctrl_msg == 1: 
          s.src0 = req.data
	elif req.ctrl_msg == 2:
          s.src1 = req.data
	elif req.ctrl_msg == 0:
          s.go = True

      if s.counter_done and not s.cpu_resp_q.is_full():
        if s.counter != 0:
          s.counter -= 1
        else:
          s.cpu_resp_q.enq( s.src0 )
	  s.go = False

  #-----------------------------------------------------------------------
  # Line Tracing: Debug Output
  #-----------------------------------------------------------------------
  def line_trace( s ):

    return "(" + str(s.cpu_ifc_resp.val) + str(s.cpu_ifc_resp.rdy) + ")"
