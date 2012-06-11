//========================================================================
// vc-SyscMsg : Syscall Message
//========================================================================
//
// The SyscMsg message type comes in two varieties: the header message
// and the body message. The header message is always sent first to
// identify the type of syscall, the number of bytes of the payload to
// follow, and an optional 64 bits for other information regarding the
// syscall, such as the file descriptor.
//
// The body message always follows a header message or a another body
// message. It only contains the payload. Both types of messages have
// bits at the front to identify whether or not the messsage is a header
// or body as well as the number of bytes in the message (not the entire
// message stream), in case all the bits of the payload field might not
// be used.
//
// Header Message Format:
//
//        132 131 128 127    96 95     64 63     32 31      0
//  +--------+-------+---------+---------+---------+---------+
//  | header |  len  |  type   | pay_sz  | special | special |
//  +--------+-------+---------+---------+---------+---------+
//
// Body Message Format:
//
//        132 131 128 127    96 95     64 63     32 31      0
//  +--------+-------+---------------------------------------+
//  | header |  len  | payload | payload | payload | payload |
//  +--------+-------+---------------------------------------+
//

`ifndef VC_SYSC_MSG_V
`define VC_SYSC_MSG_V

//------------------------------------------------------------------------
// Message fields ordered from right to left
//------------------------------------------------------------------------

// Payload field

`define VC_SYSC_MSG_PAYLOAD_SZ( p_payload_sz )                           \
  p_payload_sz

`define VC_SYSC_MSG_PAYLOAD_MSB( p_payload_sz )                          \
  ( `VC_SYSC_MSG_PAYLOAD_SZ( p_payload_sz ) - 1 )

`define VC_SYSC_MSG_PAYLOAD_FIELD( p_payload_sz )                        \
  (`VC_SYSC_MSG_PAYLOAD_MSB( p_payload_sz )):                            \
  0

// Length field

`define VC_SYSC_MSG_LEN_SZ( p_payload_sz )                               \
  ($clog2(p_payload_sz/8))

`define VC_SYSC_MSG_LEN_MSB( p_payload_sz )                              \
  (   `VC_SYSC_MSG_PAYLOAD_MSB( p_payload_sz )                           \
    + `VC_SYSC_MSG_LEN_SZ( p_payload_sz ) )

`define VC_SYSC_MSG_LEN_FIELD( p_payload_sz )                            \
  (`VC_SYSC_MSG_LEN_MSB( p_payload_sz )):                                \
  (`VC_SYSC_MSG_PAYLOAD_MSB( p_payload_sz ) + 1)

// Header field

`define VC_SYSC_MSG_HEADER_SZ( p_payload_sz ) 1
`define VC_SYSC_MSG_HEADER_HEAD               1'b0
`define VC_SYSC_MSG_HEADER_BODY               1'b1

`define VC_SYSC_MSG_HEADER_MSB( p_payload_sz )                           \
  (   `VC_SYSC_MSG_LEN_MSB( p_payload_sz )                               \
    + `VC_SYSC_MSG_HEADER_SZ( p_payload_sz ) )

`define VC_SYSC_MSG_HEADER_FIELD( p_payload_sz )                         \
  (`VC_SYSC_MSG_HEADER_MSB( p_payload_sz )):                             \
  (`VC_SYSC_MSG_LEN_MSB( p_payload_sz ) + 1)

// Total size of message

`define VC_SYSC_MSG_SZ( p_payload_sz )                                   \
  (   `VC_SYSC_MSG_HEADER_SZ( p_payload_sz )                             \
    + `VC_SYSC_MSG_LEN_SZ( p_payload_sz )                                \
    + `VC_SYSC_MSG_PAYLOAD_SZ(  p_payload_sz ) )

//------------------------------------------------------------------------
// Convert message to bits
//------------------------------------------------------------------------

module vc_SyscMsgToBits
#(
  parameter p_payload_sz = 128
)(
  // Input message

  input [`VC_SYSC_MSG_HEADER_SZ(p_payload_sz)-1:0]  header,
  input [`VC_SYSC_MSG_LEN_SZ(p_payload_sz)-1:0]     len,
  input [`VC_SYSC_MSG_PAYLOAD_SZ(p_payload_sz)-1:0] payload,

  // Output bits

  output [`VC_SYSC_MSG_SZ(p_payload_sz)-1:0] bits
);

  assign bits[`VC_SYSC_MSG_HEADER_FIELD(p_payload_sz)]  = header;
  assign bits[`VC_SYSC_MSG_LEN_FIELD(p_payload_sz)]     = len;
  assign bits[`VC_SYSC_MSG_PAYLOAD_FIELD(p_payload_sz)] = payload;

endmodule

//------------------------------------------------------------------------
// Convert message from bits
//------------------------------------------------------------------------

module vc_SyscMsgFromBits
#(
  parameter p_payload_sz = 128
)(
  // Input bits

  input [`VC_SYSC_MSG_SZ(p_payload_sz)-1:0] bits,

  // Output message

  output [`VC_SYSC_MSG_HEADER_SZ(p_payload_sz)-1:0]  header,
  output [`VC_SYSC_MSG_LEN_SZ(p_payload_sz)-1:0]     len,
  output [`VC_SYSC_MSG_PAYLOAD_SZ(p_payload_sz)-1:0] payload
);

  assign header  = bits[`VC_SYSC_MSG_HEADER_FIELD(p_payload_sz)];
  assign len     = bits[`VC_SYSC_MSG_LEN_FIELD(p_payload_sz)];
  assign payload = bits[`VC_SYSC_MSG_PAYLOAD_FIELD(p_payload_sz)];

endmodule

//------------------------------------------------------------------------
// Convert message to string
//------------------------------------------------------------------------

`ifndef SYNTHESIS
module vc_SyscMsgToStr
#(
  parameter p_payload_sz = 128
)(
  input [`VC_SYSC_MSG_SZ(p_payload_sz)-1:0] msg
);

  // Extract fields

  wire [`VC_SYSC_MSG_HEADER_SZ(p_payload_sz)-1:0]  header;
  wire [`VC_SYSC_MSG_LEN_SZ(p_payload_sz)-1:0]     len;
  wire [`VC_SYSC_MSG_PAYLOAD_SZ(p_payload_sz)-1:0] payload;

  vc_SyscMsgFromBits#(p_payload_sz) sysc_msg_from_bits
  (
    .bits    (msg),
    .header  (header),
    .len     (len),
    .payload (payload)
  );

  // Short names

  localparam c_msg_sz = `VC_SYSC_MSG_SZ(p_payload_sz);
  localparam c_head   = `VC_SYSC_MSG_HEADER_HEAD;
  localparam c_body   = `VC_SYSC_MSG_HEADER_BODY;

  // Full string sized for 41 characters

  reg [2*8-1:0]  len_str;
  reg [32*8-1:0] payload_str;

  reg [41*8-1:0] full_str;
  always @(*) begin

    $sformat( len_str,     "%x", len  );
    $sformat( payload_str, "%x", payload );

    if ( msg === {c_msg_sz{1'bx}} )
      $sformat( full_str, "x          ");
    else begin
      case ( header )
        c_head   : $sformat( full_str, "head :%s:%s", len_str, payload_str );
        c_body   : $sformat( full_str, "body :%s:%s", len_str, payload_str );
        default  : $sformat( full_str, "undefined header" );
      endcase
    end

  end

  // Tiny string sized for 2 characters

  reg [2*8-1:0] tiny_str;
  always @(*) begin

    if ( msg === {c_msg_sz{1'bx}} )
      $sformat( tiny_str, "x ");
    else begin
      case ( header )
        c_head   : $sformat( tiny_str, "he" );
        c_body   : $sformat( tiny_str, "bo" );
        default  : $sformat( tiny_str, "??" );
      endcase
    end

  end

endmodule
`endif /* SYNTHESIS */

`endif

