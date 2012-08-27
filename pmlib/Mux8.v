module Mux8
(
  input  [15:0] in4,
  input  [15:0] in5,
  input  [15:0] in6,
  input  [15:0] in7,
  input  [15:0] in0,
  input  [15:0] in1,
  input  [15:0] in2,
  input  [15:0] in3,
  input  [2:0] sel,
  output reg [15:0] out
);

 always @ (*) begin
( < )
    if ( ( sel == 0 )  ) begin
      out = in0 ;
    end
    else if ( ( sel == 1 )  ) begin
      out = in1 ;
    end
    else if ( ( sel == 2 )  ) begin
      out = in2 ;
    end
    else if ( ( sel == 3 )  ) begin
      out = in3 ;
    end
    else if ( ( sel == 4 )  ) begin
      out = in4 ;
    end
    else if ( ( sel == 5 )  ) begin
      out = in5 ;
    end
    else if ( ( sel == 6 )  ) begin
      out = in6 ;
    end
    else if ( ( sel == 7 )  ) begin
      out = in7 ;
    end
    else begin
      out = 0 ;
    end
 end


endmodule

