//========================================================================
// Test Source
//========================================================================

`ifndef VC_TEST_SOURCE_V
`define VC_TEST_SOURCE_V

`include "vc-StateElements.v"

module vc_TestSource
#(
  parameter p_msg_sz = 1,   // size of message to store in source
  parameter p_mem_sz = 1024 // size of memory that stores the messages
)(
  input  clk,
  input  reset,

  // Source message interface

  output                val,
  input                 rdy,
  output [p_msg_sz-1:0] msg,

  // Goes high once all source data has been issued

  output done
);

  //----------------------------------------------------------------------
  // Local parameters
  //----------------------------------------------------------------------

  // Size of a physical address for the memory in bits

  localparam c_physical_addr_sz = $clog2(p_mem_sz);

  //----------------------------------------------------------------------
  // State
  //----------------------------------------------------------------------

  // Memory which stores messages to send

  reg [p_msg_sz-1:0] m[p_mem_sz-1:0];

  // Index register pointing to next message to send

  wire                          index_en;
  wire [c_physical_addr_sz-1:0] index_next;
  wire [c_physical_addr_sz-1:0] index;

  vc_ERDFF_pf#(c_physical_addr_sz,{c_physical_addr_sz{1'b0}}) index_pf
  (
    .clk     (clk),
    .reset_p (reset),
    .en_p    (index_en),
    .d_p     (index_next),
    .q_np    (index)
  );

  //----------------------------------------------------------------------
  // Combinational logic
  //----------------------------------------------------------------------

  // We use a behavioral hack to easily detect when we have gone off the
  // end of the valid messages in the memory.

  assign done = ( m[index] === {p_msg_sz{1'bx}} );

  // Set the source message appropriately

  assign msg = m[index];

  // Source message interface is valid as long as we are not done

  assign val = !done;

  // The go signal is high when a message is transferred

  wire   go = val && rdy;

  // We bump the index pointer every time we successfully send a message,
  // otherwise the index stays the same.

  assign index_en   = go;
  assign index_next = index + 1;

endmodule

`endif

