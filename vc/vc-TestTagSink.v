//========================================================================
// Test Tag Sink
//========================================================================

`ifndef VC_TEST_TAG_SINK_V
`define VC_TEST_TAG_SINK_V

`include "vc-Test.v"
`include "vc-StateElements.v"

module vc_TestTagSink
#(
  parameter p_msg_nbits     = 1,    // size of message to store in source
  parameter p_num_entries   = 1024, // number of entries for each tag
  parameter p_tag_nbits     = 1,    // size of tag in bits
  parameter p_tag_offset    = 0     // offset to tag field in message in bits
)(
  input  clk,
  input  reset,

  // Sink message interface

  input                    val,
  output                   rdy,
  input  [p_msg_nbits-1:0] msg,

  // Goes high once all source data has been issued

  output done
);

  //----------------------------------------------------------------------
  // Local parameters
  //----------------------------------------------------------------------

  // Number of potential tags

  localparam c_num_tags = 1 << p_tag_nbits;

  // Total number of entries for memory including every partition

  localparam c_total_entries = c_num_tags * p_num_entries;

  // Size of index in bits

  localparam c_index_nbits = $clog2(p_num_entries);

  // Size of physical address for the memory in bits

  localparam c_physical_addr_nbits = p_tag_nbits + c_index_nbits;

  //----------------------------------------------------------------------
  // State
  //----------------------------------------------------------------------

  // Memory which stores messages to verify against those received. The
  // entire memory is partitioned into equal sections for each tag. The
  // tag of the message is used to index into the correct partition of
  // the memory.

  reg [p_msg_nbits-1:0] m[c_total_entries-1:0];

  // Data structure to hold indices for each tag partition

  wire [c_index_nbits-1:0] index_mux[c_num_tags-1:0];

  // Data structure to hold done signals for each tag partition

  wire [c_num_tags-1:0] done_array;

  // We use a generate block to instantiate a register for each index
  // corresponding to a tag partition in memory.

  genvar gen_i;

  generate
    for ( gen_i = 0; gen_i < c_num_tags; gen_i = gen_i + 1 )
    begin: index_reg_gen

      // Only enable the tag index register when a message is
      // successfully received and the tag matches the current partition.

      wire index_en = val && rdy && ( tag == gen_i );

      // The next index should always be incremented by 1

      wire [c_index_nbits-1:0] index_next = index + 1;

      // Index register pointing to next message to verify

      wire [c_index_nbits-1:0] index;

      vc_ERDFF_pf
      #(
        c_index_nbits,
        {c_index_nbits{1'b0}}
      )
      index_pf
      (
        .clk     (clk),
        .reset_p (reset),
        .en_p    (index_en),
        .d_p     (index_next),
        .q_np    (index)
      );

      // Assign index to proper entry in array

      assign index_mux[gen_i] = index;

      // We use a behavioral hack to easily detect when we have gone off the
      // end of the valid messages in the memory.

      wire [c_physical_addr_nbits-1:0] tag_addr
        = ( p_num_entries * gen_i ) + index;

      wire tag_done = ( m[tag_addr] === {p_msg_nbits{1'bx}} );

      // Assign done signal to proper entry in array

      assign done_array[gen_i] = tag_done;

    end
  endgenerate

  //----------------------------------------------------------------------
  // Combinational logic
  //----------------------------------------------------------------------

  // Shift message by offset to tag

  wire [p_msg_nbits-1:0] msg_shifted = ( msg >> p_tag_offset );

  // Determine tag from message

  wire [p_tag_nbits-1:0] tag = msg_shifted[p_tag_nbits-1:0];

  // Determine correct index based on the tag

  wire [c_index_nbits-1:0] tag_index = index_mux[tag];

  // Calculate physical address into memory

  wire [c_physical_addr_nbits-1:0] physical_addr = { tag, tag_index };

  // Expected message to compare against

  wire [p_msg_nbits-1:0] correct_bits = m[physical_addr];

  // Set global done signal if all tag done signals are high

  assign done = ( done_array == {c_num_tags{1'b1}} );

  // Sink message interface is ready as long as we are not done

  assign rdy = !done;

  // The go signal is high when a message is transferred

  wire go = val && rdy;

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
      `VC_TEST_EQ( "vc-TestTagSink", msg, correct_bits )
    end
  end

endmodule

`endif

