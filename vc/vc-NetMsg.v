//========================================================================
// vc-NetMsg : Network Message
//========================================================================
// Payload field width (payload_sz_) and source and destination field
// widths (p_srcdest_sz_) are adjustable via parameterized macro definitions.
//
// Example message format for payload_sz_ = 32, p_srcdest_sz_ = 3:
//
// 37   35 34  32 31                            0
// +------+------+-------------------------------+
// | dest | src  | payload                       |
// +------+------+-------------------------------+
//

`ifndef VC_NET_MSG_V
`define VC_NET_MSG_V

//-------------------------------------------------------------------------
// Message defines
//-------------------------------------------------------------------------

// Size of message

`define VC_NET_MSG_SZ( p_payload_sz, p_srcdest_sz )                      \
  p_payload_sz + ( 2 * p_srcdest_sz )

// Payload field

`define VC_NET_MSG_PAYLOAD_SZ( p_payload_sz, p_srcdest_sz )              \
  p_payload_sz

`define VC_NET_MSG_PAYLOAD_MSB( p_payload_sz, p_srcdest_sz )             \
  ( `VC_NET_MSG_PAYLOAD_SZ( p_payload_sz, p_srcdest_sz ) - 1 )

`define VC_NET_MSG_PAYLOAD_FIELD( p_payload_sz, p_srcdest_sz )           \
  ( `VC_NET_MSG_PAYLOAD_MSB( p_payload_sz, p_srcdest_sz ) ):             \
  0

// Source field

`define VC_NET_MSG_SRC_SZ( p_payload_sz, p_srcdest_sz )                  \
  p_srcdest_sz

`define VC_NET_MSG_SRC_MSB( p_payload_sz, p_srcdest_sz )                 \
  (   `VC_NET_MSG_PAYLOAD_MSB( p_payload_sz, p_srcdest_sz )              \
    + `VC_NET_MSG_SRC_SZ( p_payload_sz, p_srcdest_sz ) )

`define VC_NET_MSG_SRC_FIELD( p_payload_sz, p_srcdest_sz )               \
  ( `VC_NET_MSG_SRC_MSB( p_payload_sz, p_srcdest_sz ) ):                 \
  ( `VC_NET_MSG_PAYLOAD_MSB( p_payload_sz, p_srcdest_sz ) + 1 )

// Destination field

`define VC_NET_MSG_DEST_SZ( p_payload_sz, p_srcdest_sz )                 \
  p_srcdest_sz

`define VC_NET_MSG_DEST_MSB( p_payload_sz, p_srcdest_sz )                \
  (   `VC_NET_MSG_SRC_MSB( p_payload_sz, p_srcdest_sz )                  \
    + `VC_NET_MSG_DEST_SZ( p_payload_sz, p_srcdest_sz )   )

`define VC_NET_MSG_DEST_FIELD( p_payload_sz, p_srcdest_sz )              \
  ( `VC_NET_MSG_DEST_MSB( p_payload_sz, p_srcdest_sz ) ):                \
  ( `VC_NET_MSG_SRC_MSB( p_payload_sz, p_srcdest_sz ) + 1 )

// Used for printing NetMsg strings

`define VC_NET_MSG_STR_SZ ( 5 * 8 )

//-------------------------------------------------------------------------
// Convert message to bits
//-------------------------------------------------------------------------

module vc_NetMsgToBits
#(
  parameter p_payload_sz = 32,
  parameter p_srcdest_sz = 3
)
(
  // Input message

  input     [`VC_NET_MSG_DEST_SZ( p_payload_sz, p_srcdest_sz )-1:0] dest,
  input      [`VC_NET_MSG_SRC_SZ( p_payload_sz, p_srcdest_sz )-1:0] src,
  input [`VC_NET_MSG_PAYLOAD_SZ( p_payload_sz, p_src_dest_sz )-1:0] payload,

  // Output bits

  output [`VC_NET_MSG_SZ( p_payload_sz, p_srcdest_sz )-1:0] bits
);

  assign bits[`VC_NET_MSG_DEST_FIELD( p_payload_sz, p_srcdest_sz )]    = dest;
  assign bits[`VC_NET_MSG_SRC_FIELD( p_payload_sz, p_srcdest_sz )]     = src;
  assign bits[`VC_NET_MSG_PAYLOAD_FIELD( p_payload_sz, p_srcdest_sz )] = payload;

endmodule

//-------------------------------------------------------------------------
// Convert message from bits
//-------------------------------------------------------------------------

module vc_NetMsgFromBits
#(
  parameter p_payload_sz = 32,
  parameter p_srcdest_sz = 3
)
(
  // Input bits

  input  [`VC_NET_MSG_SZ( p_payload_sz, p_srcdest_sz )-1:0] bits,

  // Output message

  output    [`VC_NET_MSG_DEST_SZ( p_payload_sz, p_srcdest_sz )-1:0] dest,
  output     [`VC_NET_MSG_SRC_SZ( p_payload_sz, p_srcdest_sz )-1:0] src,
  output [`VC_NET_MSG_PAYLOAD_SZ( p_payload_sz, p_srcdest_sz )-1:0] payload
);

  assign dest    = bits[`VC_NET_MSG_DEST_FIELD( p_payload_sz, p_srcdest_sz )];
  assign src     = bits[`VC_NET_MSG_SRC_FIELD( p_payload_sz, p_srcdest_sz )];
  assign payload = bits[`VC_NET_MSG_PAYLOAD_FIELD( p_payload_sz, p_srcdest_sz )];

endmodule

//------------------------------------------------------------------------
// Convert message to string
//------------------------------------------------------------------------

`ifndef SYNTHESIS

module vc_NetMsgToStr
#(
  parameter p_payload_sz = 32,
  parameter p_srcdest_sz = 3
)
(
  input      [`VC_NET_MSG_SZ( p_payload_sz, p_srcdest_sz )-1:0] msg,
  output                               [`VC_NET_MSG_STR_SZ-1:0] str
);

  wire [7:0] ascii_lut[0:15];

  assign ascii_lut[ 0] = 8'd48;
  assign ascii_lut[ 1] = 8'd49;
  assign ascii_lut[ 2] = 8'd50;
  assign ascii_lut[ 3] = 8'd51;
  assign ascii_lut[ 4] = 8'd52;
  assign ascii_lut[ 5] = 8'd53;
  assign ascii_lut[ 6] = 8'd54;
  assign ascii_lut[ 7] = 8'd55;
  assign ascii_lut[ 8] = 8'd56;
  assign ascii_lut[ 9] = 8'd57;
  assign ascii_lut[10] = 8'd97;
  assign ascii_lut[11] = 8'd98;
  assign ascii_lut[12] = 8'd99;
  assign ascii_lut[13] = 8'd100;
  assign ascii_lut[14] = 8'd101;
  assign ascii_lut[15] = 8'd102;

  // Parse dest field

  wire [`VC_NET_MSG_DEST_SZ( p_payload_sz, p_srcdest_sz )-1:0] dest
    = msg[`VC_NET_MSG_DEST_FIELD( p_payload_sz, p_srcdest_sz )];

  // Always pad with 3 zeros at the front in case dest is less than 4 bits

  wire [`VC_NET_MSG_DEST_SZ( p_payload_sz, p_srcdest_sz )+2:0] dest_padded
    = { 3'b0, dest };

  // Parse src field

  wire [`VC_NET_MSG_SRC_SZ( p_payload_sz, p_srcdest_sz )-1:0] src
    = msg[`VC_NET_MSG_SRC_FIELD( p_payload_sz, p_srcdest_sz )];

  // Always pad with 3 zeros at the front in case src is less than 4 bits

  wire [`VC_NET_MSG_DEST_SZ( p_payload_sz, p_srcdest_sz )+2:0] src_padded
    = { 3'b0, src };

  // Parse payload field

  wire [`VC_NET_MSG_PAYLOAD_SZ( p_payload_sz, p_srcdest_sz )-1:0] payload
    = msg[`VC_NET_MSG_PAYLOAD_FIELD( p_payload_sz, p_srcdest_sz )];

  assign str = { ascii_lut[dest_padded[3:0]], ":", ascii_lut[src_padded[3:0]] };

endmodule

`endif /* SYNTHESIS */

`endif /* VC_NET_MSG_V */
