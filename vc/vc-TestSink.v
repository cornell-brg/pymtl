//========================================================================
// Test Sink
//========================================================================

`ifndef VC_TEST_SINK_V
`define VC_TEST_SINK_V

`include "vc-Test.v"
`include "vc-StateElements.v"

module vc_TestSink
#(
  parameter p_msg_sz = 1,   // size of message to store in source
  parameter p_mem_sz = 1024 // size of memory that stores the messages
)(
  input  clk,
  input  reset,

  // Sink message interface

  input                 val,
  output                rdy,
  input  [p_msg_sz-1:0] msg,

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

  // Memory which stores messages to verify against those received

  reg [p_msg_sz-1:0] m[p_mem_sz-1:0];

  // Index register pointing to next message to verify

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

  // Sink message interface is ready as long as we are not done

  assign rdy = !done;

  // We bump the index pointer every time we successfully receive a
  // message, otherwise the index stays the same.

  assign index_en   = val && rdy;
  assign index_next = index + 1;

  // The go signal is high when a message is transferred

  wire   go = val && rdy;

  //----------------------------------------------------------------------
  // Verification logic
  //----------------------------------------------------------------------

  reg [1:0] verbose;
  initial begin
    if ( !$value$plusargs( "verbose=%d", verbose ) )
      verbose = 0;
  end

  always @( posedge clk ) begin
    if ( go ) begin
      `VC_TEST_EQ( "vc-TestSink", msg, m[index] )
    end
  end

endmodule

`endif

