//========================================================================
// Verilog Components: Synchronous RAMs
//========================================================================
// This is a RAM module with synchronous reads and writes.

`ifndef VC_SRAMS_V
`define VC_SRAMS_V

//------------------------------------------------------------------------
// 1w1r SRAM
//------------------------------------------------------------------------

module vc_SRAM_1rw
#(
  parameter p_mem_sz  = 32,
  parameter p_data_sz = 32,

  // Local constants not meant to be set from outside the module
  parameter c_addr_sz    = $clog2(p_mem_sz),
  parameter c_num_bytes  = (p_data_sz+7)/8 // $ceil(p_data_sz/8)
)(
  input                   clk,
  input                   en,         // RAM enable
  input                   write_en,   // Write enable
  input [c_num_bytes-1:0] byte_en,    // Byte enable
  input   [c_addr_sz-1:0] addr,       // Access address
  input   [p_data_sz-1:0] write_data, // Write data

  output  [p_data_sz-1:0] read_data   // Read data
);

  // Memory array

  reg [p_data_sz-1:0] mem[p_mem_sz-1:0];

  // Synchronous read/write

  integer wr_i;

  reg [p_data_sz-1:0] read_data;

  always @ ( posedge clk ) begin

    if ( en ) begin

      // Read data

      read_data <= mem[addr];

      // Write data. We use a behavioral for loop here to cleanly handle
      // subword RAM writes with individual byte enables.

      if ( write_en ) begin
        for ( wr_i = 0; wr_i < p_data_sz; wr_i = wr_i + 1 ) begin
          if ( byte_en[wr_i/8] )
            mem[addr][wr_i] <= write_data[wr_i];
        end
      end

    end

  end

endmodule

`endif

