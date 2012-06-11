//========================================================================
// vc-MemRespMsg : Memory Response Message with opaque fields
//========================================================================

// TBD : Need to change the comments in here - shreesha

// Memory response messages can either be for a read or write. Read
// responses include the actual data and the number of bytes, while write
// responses currently include nothing other than the type.
//
// Message Format:
//
//    1b     calc   p_data_sz
//  +------+------+-----------+
//  | type | len  | data      |
//  +------+------+-----------+
//
// The message type is parameterized by the number of bits in the data.
// Note that the size of the length field is caclulated from the number of
// bits in the data field, and that the length field is expressed in
// _bytes_. If the value of the length field is zero, then the read is for
// the full width of the data field.
//
// For example, if the address size is 32 bits and the data size is also
// 32 bits, then the message format is as follows:
//
//   34  34 33  32 31        0
//  +------+------+-----------+
//  | type | len  | data      |
//  +------+------+-----------+
//
// The length field is two bits. A length value of one means one byte was
// read, a length value of two means read two bytes were read, and so on.
// A length value of zero means the read is for all four bytes. Note that
// not all memories will necessarily support any alignment and/or any
// value for the length field.

`ifndef VC_MEM_RESP_MSG_TAG_V
`define VC_MEM_RESP_MSG_TAG_V

//------------------------------------------------------------------------
// Message fields ordered from right to left
//------------------------------------------------------------------------

// Data field

`define VC_MEM_RESP_MSG_TAG_DATA_SZ( p_data_sz, p_tag_sz )    \
  p_data_sz

`define VC_MEM_RESP_MSG_TAG_DATA_MSB( p_data_sz,  p_tag_sz )   \
  ( `VC_MEM_RESP_MSG_TAG_DATA_SZ( p_data_sz,  p_tag_sz ) - 1 )

`define VC_MEM_RESP_MSG_TAG_DATA_FIELD( p_data_sz, p_tag_sz ) \                        
  (`VC_MEM_RESP_MSG_TAG_DATA_MSB( p_data_sz,  p_tag_sz )):     \
  0

// Length field

`define VC_MEM_RESP_MSG_TAG_LEN_SZ( p_data_sz,  p_tag_sz )     \                            
  ($clog2(p_data_sz/8))

`define VC_MEM_RESP_MSG_TAG_LEN_MSB( p_data_sz, p_tag_sz )    \                         
  (   `VC_MEM_RESP_MSG_TAG_DATA_MSB( p_data_sz, p_tag_sz )    \                         
    + `VC_MEM_RESP_MSG_TAG_LEN_SZ( p_data_sz, p_tag_sz ) )

`define VC_MEM_RESP_MSG_TAG_LEN_FIELD( p_data_sz, p_tag_sz )  \                         
  (`VC_MEM_RESP_MSG_TAG_LEN_MSB( p_data_sz, p_tag_sz )):      \
  (`VC_MEM_RESP_MSG_TAG_DATA_MSB( p_data_sz, p_tag_sz ) + 1)

// Type field

`define VC_MEM_RESP_MSG_TAG_TYPE_SZ( p_data_sz, p_tag_sz ) 3
`define VC_MEM_RESP_MSG_TAG_TYPE_READ            3'd0
`define VC_MEM_RESP_MSG_TAG_TYPE_WRITE           3'd1
`define VC_MEM_RESP_MSG_TAG_TYPE_AMOADD          3'd2
`define VC_MEM_RESP_MSG_TAG_TYPE_AMOAND          3'd3
`define VC_MEM_RESP_MSG_TAG_TYPE_AMOOR           3'd4
`define VC_MEM_RESP_MSG_TAG_TYPE_AMOXCH          3'd5

`define VC_MEM_RESP_MSG_TAG_TYPE_MSB( p_data_sz,p_tag_sz )   \
  (   `VC_MEM_RESP_MSG_TAG_LEN_MSB( p_data_sz,  p_tag_sz )     \
    + `VC_MEM_RESP_MSG_TAG_TYPE_SZ( p_data_sz, p_tag_sz ) )

`define VC_MEM_RESP_MSG_TAG_TYPE_FIELD( p_data_sz, p_tag_sz ) \
  (`VC_MEM_RESP_MSG_TAG_TYPE_MSB( p_data_sz,  p_tag_sz )):     \
  (`VC_MEM_RESP_MSG_TAG_LEN_MSB( p_data_sz, p_tag_sz ) + 1)

// Tag field

`define VC_MEM_RESP_MSG_TAG_TAG_SZ( p_data_sz,  p_tag_sz )     \                            
  p_tag_sz

`define VC_MEM_RESP_MSG_TAG_TAG_MSB( p_data_sz, p_tag_sz )    \                         
  (   `VC_MEM_RESP_MSG_TAG_TYPE_MSB( p_data_sz, p_tag_sz )    \                         
    + `VC_MEM_RESP_MSG_TAG_TAG_SZ( p_data_sz, p_tag_sz ) )

`define VC_MEM_RESP_MSG_TAG_TAG_FIELD( p_data_sz, p_tag_sz )  \                         
  (`VC_MEM_RESP_MSG_TAG_TAG_MSB( p_data_sz, p_tag_sz )):      \
  (`VC_MEM_RESP_MSG_TAG_TYPE_MSB( p_data_sz, p_tag_sz ) + 1)

// Total size of message

`define VC_MEM_RESP_MSG_TAG_SZ( p_data_sz, p_tag_sz )                                 \
  (   `VC_MEM_RESP_MSG_TAG_TAG_SZ( p_data_sz, p_tag_sz  )                             \
    + `VC_MEM_RESP_MSG_TAG_TYPE_SZ( p_data_sz, p_tag_sz  )                             \
    + `VC_MEM_RESP_MSG_TAG_LEN_SZ(  p_data_sz, p_tag_sz  )                             \
    + `VC_MEM_RESP_MSG_TAG_DATA_SZ( p_data_sz, p_tag_sz  ) )

//------------------------------------------------------------------------
// Convert message to bits
//------------------------------------------------------------------------

module vc_MemRespMsgTagToBits
#(
  parameter p_data_sz = 32,
  parameter p_tag_sz  = 2
)(
  // Input message

  input [`VC_MEM_RESP_MSG_TAG_TAG_SZ(p_data_sz,p_tag_sz)-1:0]  tag,
  input [`VC_MEM_RESP_MSG_TAG_TYPE_SZ(p_data_sz,p_tag_sz)-1:0] type,
  input [`VC_MEM_RESP_MSG_TAG_LEN_SZ(p_data_sz,p_tag_sz)-1:0]  len,
  input [`VC_MEM_RESP_MSG_TAG_DATA_SZ(p_data_sz,p_tag_sz)-1:0] data,

  // Output bits

  output [`VC_MEM_RESP_MSG_TAG_SZ(p_data_sz,p_tag_sz)-1:0] bits
);

  assign bits[`VC_MEM_RESP_MSG_TAG_TAG_FIELD(p_data_sz,p_tag_sz)]  = tag;
  assign bits[`VC_MEM_RESP_MSG_TAG_TYPE_FIELD(p_data_sz,p_tag_sz)] = type;
  assign bits[`VC_MEM_RESP_MSG_TAG_LEN_FIELD(p_data_sz,p_tag_sz)]  = len;
  assign bits[`VC_MEM_RESP_MSG_TAG_DATA_FIELD(p_data_sz,p_tag_sz)] = data;

endmodule

//------------------------------------------------------------------------
// Convert message from bits
//------------------------------------------------------------------------

module vc_MemRespMsgTagFromBits
#(
  parameter p_data_sz = 32,
  parameter p_tag_sz  = 2
)(
  // Input bits

  input [`VC_MEM_RESP_MSG_TAG_SZ(p_data_sz,p_tag_sz)-1:0] bits,

  // Output message

  output [`VC_MEM_RESP_MSG_TAG_TAG_SZ(p_data_sz,p_tag_sz)-1:0] tag,
  output [`VC_MEM_RESP_MSG_TAG_TYPE_SZ(p_data_sz,p_tag_sz)-1:0] type,
  output [`VC_MEM_RESP_MSG_TAG_LEN_SZ(p_data_sz,p_tag_sz)-1:0] len,
  output [`VC_MEM_RESP_MSG_TAG_DATA_SZ(p_data_sz,p_tag_sz)-1:0] data
);

  assign tag = bits[`VC_MEM_RESP_MSG_TAG_TAG_FIELD(p_data_sz,p_tag_sz)];
  assign type = bits[`VC_MEM_RESP_MSG_TAG_TYPE_FIELD(p_data_sz,p_tag_sz)];
  assign len  = bits[`VC_MEM_RESP_MSG_TAG_LEN_FIELD(p_data_sz,p_tag_sz)];
  assign data = bits[`VC_MEM_RESP_MSG_TAG_DATA_FIELD(p_data_sz,p_tag_sz)];

endmodule

//------------------------------------------------------------------------
// Convert message to string
//------------------------------------------------------------------------

`ifndef SYNTHESIS
module vc_MemRespMsgTagToStr
#(
  parameter p_data_sz = 32,
  parameter p_tag_sz  = 2
)(
  input [`VC_MEM_RESP_MSG_TAG_SZ(p_data_sz,p_tag_sz)-1:0] msg
);

  // Extract fields

  wire [`VC_MEM_RESP_MSG_TAG_TAG_SZ(p_data_sz,p_tag_sz)-1:0]  tag;
  wire [`VC_MEM_RESP_MSG_TAG_TYPE_SZ(p_data_sz,p_tag_sz)-1:0] type;
  wire [`VC_MEM_RESP_MSG_TAG_LEN_SZ(p_data_sz,p_tag_sz)-1:0]  len;
  wire [`VC_MEM_RESP_MSG_TAG_DATA_SZ(p_data_sz,p_tag_sz)-1:0] data;

  vc_MemRespMsgTagFromBits#(p_data_sz) mem_resp_msg_from_bits
  (
    .bits (msg),
    .tag  (tag),
    .type (type),
    .len  (len),
    .data (data)
  );

  // Short names

  localparam c_msg_sz = `VC_MEM_RESP_MSG_TAG_SZ(p_data_sz,p_tag_sz);
  localparam c_read   = `VC_MEM_RESP_MSG_TAG_TYPE_READ;
  localparam c_write  = `VC_MEM_RESP_MSG_TAG_TYPE_WRITE;
  localparam c_amoadd = `VC_MEM_RESP_MSG_TAG_TYPE_AMOADD;
  localparam c_amoand = `VC_MEM_RESP_MSG_TAG_TYPE_AMOAND;
  localparam c_amoor  = `VC_MEM_RESP_MSG_TAG_TYPE_AMOOR;
  localparam c_amoxch = `VC_MEM_RESP_MSG_TAG_TYPE_AMOXCH;

  // Full string sized for 12 characters

  reg [1*8-1:0] len_str;
  reg [4*8-1:0] data_str;

  reg [12*8-1:0] full_str;
  always @(*) begin

    $sformat( len_str,  "%x", len  );
    $sformat( data_str, "%x", data );

    if ( msg === {c_msg_sz{1'bx}} )
      $sformat( full_str, "x        ");
    else begin
      case ( type )
        c_read   : $sformat( full_str, "rd   :%s:%s", len_str, data_str );
        c_write  : $sformat( full_str, "wr          " );
        c_amoadd : $sformat( full_str, "aadd :%s:%s", len_str, data_str );
        c_amoand : $sformat( full_str, "aand :%s:%s", len_str, data_str );
        c_amoor  : $sformat( full_str, "aor  :%s:%s", len_str, data_str );
        c_amoxch : $sformat( full_str, "axch :%s:%s", len_str, data_str );
        default  : $sformat( full_str, "undefined type" );
      endcase
    end

  end

  // Tiny string sized for 2 characters

  reg [2*8-1:0] tiny_str;
  always @(*) begin

    if ( msg === {c_msg_sz{1'bx}} )
      $sformat( tiny_str, "x ");
    else begin
      case ( type )
        c_read   : $sformat( tiny_str, "rd" );
        c_write  : $sformat( tiny_str, "wr" );
        c_amoadd : $sformat( tiny_str, "a+" );
        c_amoand : $sformat( tiny_str, "a&" );
        c_amoor  : $sformat( tiny_str, "a+" );
        c_amoxch : $sformat( tiny_str, "ax" );
        default  : $sformat( tiny_str, "??" );
      endcase
    end

  end

endmodule
`endif /* SYNTHESIS */

`endif /* VC_MEM_RESP_MSG_TAG_V */

