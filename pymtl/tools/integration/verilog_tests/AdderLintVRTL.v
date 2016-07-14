//------------------------------------------------------------------------
// Adder with Lint Problem
//------------------------------------------------------------------------
module AdderLintVRTL
#(
  parameter nbits = 1
)(
  input              clk,
  input              reset,
  input  [nbits-1:0] in0,
  input  [nbits-1:0] in1,
  input              cin,
  output [nbits-1:0] out,
  output             cout
);

  reg [nbits:0] temp;

  always @( * ) begin
    temp = (in0 + in1) + cin;
  end

  assign cout = temp[nbits];
  assign out  = temp[nbits-1:0];

endmodule
