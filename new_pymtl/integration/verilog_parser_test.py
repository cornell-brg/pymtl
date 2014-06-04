#=======================================================================
# verilog_parser
#=======================================================================

import pytest
from   verilog_parser import header_parser

#-----------------------------------------------------------------------
# test cases
#-----------------------------------------------------------------------

def a(): return """\
module tester;
endmodule
"""

def b(): return """\
module vc_QueueCtrl1
(
  input  clk, reset,
  input  enq_val,
  output enq_rdy,
  output deq_val,
  input  deq_rdy,
  output wen,
  output bypass_mux_sel
);
endmodule
"""

def c(): return """\
module vc_QueueCtrl1
(
  input  clk, reset,
  input  enq_val,
  output reg enq_rdy,
  output reg deq_val,
  input  deq_rdy,
  output reg wen,
  output bypass_mux_sel
);
endmodule
"""

def d(): return """\
module vc_QueueCtrl1
(
  input  [0  :0] clk, reset,
  input  [1  :0] enq_val,
  output [0  :0] enq_rdy,
  output [4  :0] deq_val,
  input  [0  :0] deq_rdy,
  output [0  :0] wen,
  output [2-1:0] bypass_mux_sel
);
endmodule
"""

def e(): return """\
//module vc_QueueCtrl1 #( parameter TYPE = `VC_QUEUE_NORMAL )
module vc_QueueCtrl1 //#( parameter TYPE = `VC_QUEUE_NORMAL )
(
  input  clk, reset,
  input  enq_val,        // Enqueue data is valid
  output enq_rdy,        // Ready for producer to do an enqueue
  output deq_val,        // Dequeue data is valid
  input  deq_rdy,        // Consumer is ready to do a dequeue
  output wen,            // Write en signal to wire up to storage element
  output bypass_mux_sel  // Used to control bypass mux for bypass queues
);
endmodule
"""

def f(): return """\
module vc_QueueCtrl1 #( parameter TYPE = `VC_QUEUE_NORMAL )
(
  input  clk, reset,
  input  enq_val,        // Enqueue data is valid
  output enq_rdy,        // Ready for producer to do an enqueue
  output deq_val,        // Dequeue data is valid
  input  deq_rdy,        // Consumer is ready to do a dequeue
  output wen,            // Write en signal to wire up to storage element
  output bypass_mux_sel  // Used to control bypass mux for bypass queues
);
endmodule
"""

def g(): return """\
// comment
module simple /* comment */
(
  input  in, // comment
  /* comment */
  output out // comment
);
endmodule
"""

def h(): return """\
  module vc_RoundRobinArbChain
  #(
    parameter NUM_REQS           = 2,
    parameter RESET_PRIORITY_VAL = 1  // (one-hot) 1 indicates which req
                                      //   has highest priority on reset
  )(
    input                 clk,
    input                 reset,
    input                 kin,    // Kill in
    input  [NUM_REQS-1:0] reqs,   // 1 = making a request, 0 = no request
    output [NUM_REQS-1:0] grants, // (one-hot) 1 is req won grant
    output                kout    // Kill out
  );
  endmodule
"""

def i(): return """\
  module mod_a #( parameter a = 2, parameter b = 3 )
  (
    input  in,
    output out
  );
  endmodule
"""

def j(): return """\
  module mod_a
  #( parameter a = 2 )
  (
    input  in,
    output out
  );
  endmodule

  module mod_b
  #( parameter a = 2, parameter b = 2)
  (
    input  in,
    output out
  );
  endmodule
"""

def y(): return """\
module fulladder ( carry, sum, in1, in2, in3 );
endmodule
"""

def x(): return """\
module fulladder ( carry, sum, in1, in2, in3 );
  input in1, in2, in3;
  output carry, sum;
  //xor U5 ( in1, n3, sum );
endmodule
"""

#-----------------------------------------------------------------------
# test_simple
#-----------------------------------------------------------------------
@pytest.mark.parametrize( 'src',
  [a, b, c, d, e, f, g, h, i, j, y, x]
)
def test_simple( src ):
  source = header_parser()
  source.parseString( src(), parseAll=True )


