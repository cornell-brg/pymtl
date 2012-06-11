//========================================================================
// Tests for Crossbar
//========================================================================

`ifndef VC_CROSSBAR_T_V
`define VC_CROSSBAR_T_V

`include "vc-Crossbar.v"
`include "vc-Test.v"

module tester;

  localparam MSG_SZ = 32;

  `VC_TEST_SUITE_BEGIN("vc-Crossbar")

  reg [MSG_SZ-1:0]  in0 = 32'hdeadbeef;
  reg [MSG_SZ-1:0]  in1 = 32'hbeeff00d;
  reg [MSG_SZ-1:0]  in2 = 32'hcafebabe; 

  reg [1:0]         sel0;
  reg [1:0]         sel1;
  reg [1:0]         sel2;
 
  wire [MSG_SZ-1:0] out0;
  wire [MSG_SZ-1:0] out1;
  wire [MSG_SZ-1:0] out2;
 
  vc_Crossbar#(MSG_SZ) xbar
  (
    .in0  (in0),
    .in1  (in1),
    .in2  (in2),
    .sel0 (sel0),
    .sel1 (sel1),
    .sel2 (sel2),
    .out0 (out0),
    .out1 (out1),
    .out2 (out2)
  );

  task do_test
  (
    input [8*8-1:0]    test_case_str,
    input [1:0]        test_sel0,
    input [1:0]        test_sel1,
    input [1:0]        test_sel2,
    input [MSG_SZ-1:0] correct_out0,
    input [MSG_SZ-1:0] correct_out1,
    input [MSG_SZ-1:0] correct_out2
  );
  begin
    sel0 = test_sel0;
    sel1 = test_sel1;
    sel2 = test_sel2;
    #25;
    `VC_TEST_EQ3(test_case_str,
                 out0, correct_out0,
                 out1, correct_out1,
                 out2, correct_out2)
    #25; 
  end
  endtask

  `VC_TEST_CASE_BEGIN(1, "Crossbar")
  begin
    do_test("sel0 = 0, sel1 = 1, sel2 = 2",
      3'd0, 3'd1, 3'd2,
      32'hdeadbeef, 32'hbeeff00d, 32'hcafebabe);
    do_test("sel0 = 0, sel1 = 2, sel2 = 1",
      3'd0, 3'd2, 3'd1,
      32'hdeadbeef, 32'hcafebabe, 32'hbeeff00d);
    do_test("sel0 = 1, sel1 = 2, sel2 = 0",
      3'd1, 3'd2, 3'd0,
      32'hbeeff00d, 32'hcafebabe, 32'hdeadbeef);
    do_test("sel0 = 1, sel1 = 0, sel2 = 2",
      3'd1, 3'd0, 3'd2,
      32'hbeeff00d, 32'hdeadbeef, 32'hcafebabe);
    do_test("sel0 = 2, sel1 = 1, sel2 = 0",
      3'd2, 3'd1, 3'd0,
      32'hcafebabe, 32'hbeeff00d, 32'hdeadbeef);
    do_test("sel0 = 2, sel1 = 0, sel2 = 1",
      3'd2, 3'd0, 3'd1,
      32'hcafebabe, 32'hdeadbeef, 32'hbeeff00d);  
  end	
  `VC_TEST_CASE_END

  `VC_TEST_SUITE_END(1)
endmodule

`endif
