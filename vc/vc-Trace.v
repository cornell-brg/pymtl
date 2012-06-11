//========================================================================
// Trace tools
//========================================================================

`ifndef VC_TRACE_V
`define VC_TRACE_V

//------------------------------------------------------------------------
// vc_TraceWithValRdy
//------------------------------------------------------------------------

module vc_TraceWithValRdy
#(
  parameter integer NUMBITS      = 1,
  parameter integer NUMCHARS     = 2,
  parameter integer FORMAT_CHARS = 2,
  parameter [(FORMAT_CHARS<<3)-1:0] FORMAT = "%x"
)(
  input  val,
  input  rdy,
  input  [(NUMCHARS<<3)-1:0] istr,
  input  [NUMBITS-1:0]       bits
);

  reg [(NUMCHARS<<3)-1:0] valid_str;

  always @(*)
  begin
    $sformat( valid_str, FORMAT, bits );
  end

  reg [(NUMCHARS<<3)-1:0] str;

  always @(*)
  begin
    if ( (rdy == 1'b1) && (val == 1'b1)  )
      str = valid_str;
    else if ( (rdy == 1'b1) && (val == 1'b0)  )
      str = { ".", {(NUMCHARS-1){" "}} };
    else if ( (rdy == 1'b0) && (val == 1'b1)  )
      str = { ",", {(NUMCHARS-1){" "}} };
    else if ( (rdy == 1'b0) && (val == 1'b0)  )
      str = { ";", {(NUMCHARS-1){" "}} };
    else
      str = { "x", {(NUMCHARS-1){" "}} };
  end

endmodule

//------------------------------------------------------------------------
// vc_TraceBit
//------------------------------------------------------------------------

module vc_TraceBit
#(
  parameter [7:0] TRUE_CHAR  = "*",
  parameter [7:0] FALSE_CHAR = " "
)(
  input bit
);

  reg [7:0] str;

  always @(*)
  begin
    if ( bit == 1'b1 )
      str = TRUE_CHAR;
    else if ( bit == 1'b0 )
      str = FALSE_CHAR;
    else
      str = "x";
  end

endmodule

//------------------------------------------------------------------------
// vc_TraceMutexBits
//------------------------------------------------------------------------

module vc_TraceMutexBits
#(
  parameter integer             NUMBITS  = 1,
  parameter integer             NUMCHARS = 1,
  parameter [(NUMCHARS<<3)-1:0] STR0 = "?",
  parameter [(NUMCHARS<<3)-1:0] STR1 = "?",
  parameter [(NUMCHARS<<3)-1:0] STR2 = "?",
  parameter [(NUMCHARS<<3)-1:0] STR3 = "?",
  parameter [(NUMCHARS<<3)-1:0] STR4 = "?",
  parameter [(NUMCHARS<<3)-1:0] STR5 = "?",
  parameter [(NUMCHARS<<3)-1:0] STR6 = "?",
  parameter [(NUMCHARS<<3)-1:0] STR7 = "?"
)(
  input [7:0] bits
);

  reg [(NUMCHARS<<3)-1:0] str;

  integer numberTrue;
  integer numberX ;
  always @(*)
  begin
    str = {NUMCHARS{" "}};
    numberTrue = 0;
    numberX    = 0;

    if ( bits[0] && ( 0 < NUMBITS ) )
     begin
      numberTrue = numberTrue + 1;
      str = STR0;
     end
    else if ( ( bits[0] === 1'bx ) && ( 0 < NUMBITS ) )
      numberX = numberX + 1;

    if ( bits[1] && ( 1 < NUMBITS ) )
     begin
      numberTrue = numberTrue + 1;
      str = STR1;
     end
    else if ( ( bits[1] === 1'bx ) && ( 1 < NUMBITS ) )
      numberX = numberX + 1;

    if ( bits[2] && ( 2 < NUMBITS ) )
     begin
      numberTrue = numberTrue + 1;
      str = STR2;
     end
    else if ( ( bits[2] === 1'bx ) && ( 2 < NUMBITS ) )
      numberX = numberX + 1;

    if ( bits[3] && ( 3 < NUMBITS ) )
     begin
      numberTrue = numberTrue + 1;
      str = STR3;
     end
    else if ( ( bits[3] === 1'bx ) && ( 3 < NUMBITS ) )
      numberX = numberX + 1;

    if ( bits[4] && ( 4 < NUMBITS ) )
     begin
      numberTrue = numberTrue + 1;
      str = STR4;
     end
    else if ( ( bits[4] === 1'bx ) && ( 4 < NUMBITS ) )
      numberX = numberX + 1;

    if ( bits[5] && ( 5 < NUMBITS ) )
     begin
      numberTrue = numberTrue + 1;
      str = STR5;
     end
    else if ( ( bits[5] === 1'bx ) && ( 5 < NUMBITS ) )
      numberX = numberX + 1;

    if ( bits[6] && ( 6 < NUMBITS ) )
     begin
      numberTrue = numberTrue + 1;
      str = STR6;
     end
    else if ( ( bits[6] === 1'bx ) && ( 6 < NUMBITS ) )
      numberX = numberX + 1;

    if ( bits[7] && ( 7 < NUMBITS ) )
     begin
      numberTrue = numberTrue + 1;
      str = STR7;
     end
    else if ( ( bits[7] === 1'bx ) && ( 7 < NUMBITS ) )
      numberX = numberX + 1;

    if ( numberTrue > 1 )
      str = "!";

    if ( numberX > 0 )
      str = "x";

  end

endmodule

`endif

