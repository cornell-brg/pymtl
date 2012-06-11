//========================================================================
// Verilog Components: Misc
//========================================================================

`ifndef VC_MISC_V
`define VC_MISC_V

`include "vc-StateElements.v"

//------------------------------------------------------------------------
// Decoder
//------------------------------------------------------------------------

module vc_Decoder
#(
  parameter IN_SZ  = 2,
  parameter OUT_SZ = 4
)(
  input  [IN_SZ-1:0]  in,
  output [OUT_SZ-1:0] out
);

  genvar i;
  generate
    for ( i = 0; i < OUT_SZ; i = i + 1 )
    begin : decode
      assign out[i] = (in == i);
    end
  endgenerate

endmodule

//------------------------------------------------------------------------
// Tri-State Buffer
//------------------------------------------------------------------------

module vc_TriBuf #( parameter IN_SZ = 1 )
(
  input  [IN_SZ-1:0] in,
  input              oe,
  output [IN_SZ-1:0] out
);

  assign out = oe ? in : {IN_SZ{1'bz}};

endmodule

//------------------------------------------------------------------------
// Partitioned Tri-State Buffer
//------------------------------------------------------------------------

module vc_PartitionedTriBuf
#(
  parameter IN_SZ        = 1,
  parameter PARTITION_SZ = 1
)
(
  input  [IN_SZ-1:0]                in,
  input  [(IN_SZ/PARTITION_SZ)-1:0] oe,
  output [PARTITION_SZ-1:0]         out
);

  localparam NUM_PARTITIONS = ( IN_SZ / PARTITION_SZ );

  genvar partNum;
  generate
    for ( partNum = 0; partNum < NUM_PARTITIONS; partNum = partNum + 1 )
    begin : part
      assign out = oe[partNum] ? in[(partNum*PARTITION_SZ)+:PARTITION_SZ]
                                : {PARTITION_SZ{1'bz}};
    end
  endgenerate

endmodule

//------------------------------------------------------------------------
// Force One Hot
//------------------------------------------------------------------------
// If the input is all zeros then arbitrarily makes one of the signals
// one. We could add extra logic later to keep the same signal asserted
// which might reduce power?

module vc_ForceOneHot #( parameter IN_SZ = 2 )
(
  input  [IN_SZ-1:0] in,
  output [IN_SZ-1:0] out
);

  assign out[IN_SZ-1:1] = in[IN_SZ-1:1];
  assign out[0] = ( |in ) ? in[0] : 1'b1;

endmodule

//------------------------------------------------------------------------
// Counter
//------------------------------------------------------------------------
// Up/Down counter. If both increment and decrement are set then the
// counter does not change. Increment and decrement are ignored if
// init_count_val is set. comb_next is combinational from
// init_count_val/inc/dec

module vc_Counter_pf
#(
  parameter COUNT_SZ    = 4, // Bitwidth of counter
  parameter RESET_VALUE = 0  // Value to reset counter to
)(
  input                 clk,
  input                 reset_p,
  input                 init_count_val_p,  // Is the init_count valid?
  input  [COUNT_SZ-1:0] init_count_p,      // What is init counter value?
  input                 increment_p,       // Increment the counter
  input                 decrement_p,       // Decrement the counter
  output [COUNT_SZ-1:0] count_np,          // What is current count?
  output [COUNT_SZ-1:0] count_next         // What is next count?
);

  localparam [COUNT_SZ-1:0] CONST_ONE = 1;

  // State

  vc_RDFF_pf#(COUNT_SZ,RESET_VALUE) count_pf
  (
    .clk     (clk),
    .reset_p (reset_p),
    .d_p     (count_next),
    .q_np    (count_np)
  );

  // Logic

  wire do_increment_p = !init_count_val_p & increment_p  & !decrement_p;
  wire do_decrement_p = !init_count_val_p & !increment_p &  decrement_p;

  assign count_next = do_increment_p   ? count_np + CONST_ONE
                    : do_decrement_p   ? count_np - CONST_ONE
                    : init_count_val_p ? init_count_p
                    :                    count_np;

endmodule

//------------------------------------------------------------------------
// Pseudo Random Number Generator
//------------------------------------------------------------------------

module vc_RandomNumberGenerator
#(
  parameter OUT_SZ = 4, // Bitwidth of output
  parameter SEED   = 0  // Random seed, should be 32 bits
)(
  input                   clk,
  input                   reset_p,
  input                   next_p,   // Generate next value
  output reg [OUT_SZ-1:0] out_np    // Current random num
);

  // State

  wire        rand_num_en;
  wire [31:0] rand_num_next;
  wire [31:0] rand_num;

  vc_ERDFF_pf#(32,SEED) rand_num_pf
  (
    .clk     (clk),
    .reset_p (reset_p),
    .en_p    (rand_num_en),
    .d_p     (rand_num_next),
    .q_np    (rand_num)
  );

  // Logic for a simple random num generator using the Tausworthe alog

  wire [31:0] temp = ((rand_num >> 17) ^ rand_num);
  assign rand_num_next = ((temp << 15) ^ temp);
  assign rand_num_en = next_p;

  // We xor higher order bits to create smaller output numbers

  integer i;
  always @(*)
  begin
    out_np = rand_num[OUT_SZ-1:0];
    for ( i = (2*OUT_SZ-1); i < 31; i = i + OUT_SZ )
      out_np = out_np ^ rand_num[i-:OUT_SZ];
  end

endmodule

`endif

