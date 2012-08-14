//=========================================================================
// RTL Model of GCD Unit
//-------------------------------------------------------------------------
//
`include "vc-Test.v"
`include "vc-TestSource.v"
`include "vc-TestSink.v"
`include "vc-StateElements.v"
`include "gcdGCDUnit_rtl.v"
`define functional

module gcdTestHarness_rtl;

  `VC_TEST_SUITE_BEGIN( "gcdGCDUnit_rtl" )
  
  //--------------------------------------------------------------------
  // Instantiate modules
  //--------------------------------------------------------------------

  // Reset register

  reg  reset_ext;
  wire reset;
  
  vc_DFF_pf#(1) reset_pf
  ( 
    .clk  (clk), 
    .d_p  (reset_ext), 
    .q_np (reset) 
  );
  
  // Test source
  
  wire [31:0] src_bits;
  wire [15:0] src_bits_A = src_bits[31:16];
  wire [15:0] src_bits_B = src_bits[15:0];
  wire        src_val;
  wire        src_rdy;
  wire        src_done;
 
  vc_TestSource#(32) src
  (
    .clk   (clk),
    .reset (reset),
    .msg   (src_bits),
    .val   (src_val),
    .rdy   (src_rdy),
    .done  (src_done)
  );

  // GCD unit
  
  wire [15:0] result_bits_data;
  wire        result_val;
  wire        result_rdy;
  
  gcdGCDUnit_rtl#(16) gcd
  ( 
    .clk              (clk),
    .reset            (reset),

    .operands_bits_A  (src_bits_A),
    .operands_bits_B  (src_bits_B),  
    .operands_val     (src_val),
    .operands_rdy     (src_rdy),

    .result_bits_data (result_bits_data), 
    .result_val       (result_val),
    .result_rdy       (result_rdy)

  );

  // Test sink
  
  wire sink_done;
  
  vc_TestSink#(16) sink
  (
    .clk   (clk),
    .reset (reset),
    .msg   (result_bits_data),
    .val   (result_val),
    .rdy   (result_rdy),
    .done  (sink_done)    
  );

  wire done = src_done && sink_done;
  
  //--------------------------------------------------------------------
  // Run tests
  //--------------------------------------------------------------------

  initial
  begin
    $dumpfile("check.vcd");
    $dumpvars;
  end

  initial
  begin

    //$vcdpluson;

    src.m[0] = { 16'd27,  16'd15  }; sink.m[0] = { 16'd3  };
    src.m[1] = { 16'd21,  16'd49  }; sink.m[1] = { 16'd7  };
    src.m[2] = { 16'd25,  16'd30  }; sink.m[2] = { 16'd5  };
    src.m[3] = { 16'd19,  16'd27  }; sink.m[3] = { 16'd1  };
    src.m[4] = { 16'd40,  16'd40  }; sink.m[4] = { 16'd40 };
    src.m[5] = { 16'd250, 16'd190 }; sink.m[5] = { 16'd10 };
    src.m[6] = { 16'd5,   16'd250 }; sink.m[6] = { 16'd5  };
    src.m[7] = { 16'd0,   16'd0   }; sink.m[7] = { 16'd0  };
    
    //#2000 $vcdplusoff;
  end

  `VC_TEST_CASE_BEGIN( 0, "gcdGCDUnit_rtl" )
  begin

    // Strobe reset
    #1;   reset_ext = 1'b1;
    #20;  reset_ext = 1'b0;

    // Run long enough that tests should be done
    #1500;

    // Check to make sure it is actually done
    `VC_TEST_CHECK( "Is sink finished?", done )
    
  end
  `VC_TEST_CASE_END

  `VC_TEST_SUITE_END( 1 )
endmodule
