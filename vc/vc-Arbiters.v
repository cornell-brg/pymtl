//========================================================================
// Verilog Components: Arbiters
//========================================================================
// There are three basic arbiter components which are provided in this
// file: vc_FixedArbChain, vc_VariableArbChain, vc_RoundRobinArbChain.
// These basic components can be combined in various ways to create the
// desired arbiter.

`ifndef VC_ARBITERS_V
`define VC_ARBITERS_V

`include "vc-StateElements.v"

//------------------------------------------------------------------------
// vc_FixedArbChain
//------------------------------------------------------------------------
// reqs[0] has the highest priority, reqs[1] has the second
// highest priority, etc.

module vc_FixedArbChain #( parameter NUM_REQS = 2 )
(
  input                 kin,    // Kill in
  input  [NUM_REQS-1:0] reqs,   // 1 = making a request, 0 = no request
  output [NUM_REQS-1:0] grants, // (one-hot) 1 indicates req won grant
  output                kout    // Kill out
);

  // The internal kills signals essentially form a kill chain from the
  // highest priority to the lowest priority requester. The highest
  // priority requster (say requester i) which is actually making a
  // request sets the kill signal for the next requester to one (ie
  // kills[i+1]) and then this kill signal is propagated to all lower
  // priority requesters.

  wire [NUM_REQS:0] kills;
  assign kills[0] = 1'b0;

  // The per requester logic first computes the grant signal and then
  // computes the kill signal for the next requester.

  wire [NUM_REQS-1:0] grants_int;

  genvar i;
  generate
  for ( i = 0; i < NUM_REQS; i = i + 1 )
  begin : per_req_logic

    // Grant is true if this requester is not killed and it is actually
    // making a request.

    assign grants_int[i] = !kills[i] && reqs[i];

    // Kill is true if this requester was either killed or it received
    // the grant.

    assign kills[i+1] = kills[i] || grants_int[i];

  end
  endgenerate

  // We AND kin into the grant and kout signals afterwards so that we can
  // begin doing the arbitration before we know kin. This also allows us
  // to build hybrid tree-ripple arbiters out of vc_FixedArbChain
  // components.

  assign grants = grants_int & {NUM_REQS{~kin}};
  assign kout   = kills[NUM_REQS] || kin;

endmodule

//------------------------------------------------------------------------
// vc_FixedArb
//------------------------------------------------------------------------
// reqs[0] has the highest priority, reqs[1] has the second highest
// priority, etc.

module vc_FixedArb #( parameter NUM_REQS = 2 )
(
  input  [NUM_REQS-1:0] reqs,  // 1 = making a request, 0 = no request
  output [NUM_REQS-1:0] grants // (one-hot) 1 indicates which req won grant
);

  wire dummy_kout;

  vc_FixedArbChain#(NUM_REQS) fixedArbChain
  (
    .kin    (1'b0),
    .reqs   (reqs),
    .grants (grants),
    .kout   (dummy_kout)
  );

endmodule

//------------------------------------------------------------------------
// vc_VariableArbChain
//------------------------------------------------------------------------
// The input priority signal is a one-hot signal where the one indicates
// which request should be given highest priority.

module vc_VariableArbChain #( parameter NUM_REQS = 2 )
(
  input                 kin,       // Kill in
  input  [NUM_REQS-1:0] priority,  // (one-hot) 1 is req w/ highest pri
  input  [NUM_REQS-1:0] reqs,      // 1 = making a request, 0 = no request
  output [NUM_REQS-1:0] grants,    // (one-hot) 1 is req won grant
  output                kout       // Kill out
);

  // The internal kills signals essentially form a kill chain from the
  // highest priority to the lowest priority requester. Unliked the fixed
  // arb, the priority input is used to determine which request has the
  // highest priority. We could use a circular kill chain, but static
  // timing analyzers would probably consider it a combinational loop
  // (which it is) and choke. Instead we replicate the kill chain. See
  // Principles and Practices of Interconnection Networks, Dally +
  // Towles, p354 for more info.

  wire [2*NUM_REQS:0] kills;
  assign kills[0] = 1'b1;

  wire [2*NUM_REQS-1:0] priority_int = { {NUM_REQS{1'b0}}, priority };
  wire [2*NUM_REQS-1:0] reqs_int     = { reqs, reqs };
  wire [2*NUM_REQS-1:0] grants_int;

  // The per requester logic first computes the grant signal and then
  // computes the kill signal for the next requester.

  localparam NUM_REQS_x2 = (NUM_REQS << 1);
  genvar i;
  generate
  for ( i = 0; i < 2*NUM_REQS; i = i + 1 )
  begin : per_req_logic

    // If this is the highest priority requester, then we ignore the
    // input kill signal, otherwise grant is true if this requester is
    // not killed and it is actually making a request.

    assign grants_int[i]
      = priority_int[i] ? reqs_int[i] : (!kills[i] && reqs_int[i]);

    // If this is the highest priority requester, then we ignore the
    // input kill signal, otherwise kill is true if this requester was
    // either killed or it received the grant.

    assign kills[i+1]
      = priority_int[i] ? grants_int[i] : (kills[i] || grants_int[i]);

  end
  endgenerate

  // To calculate final grants we OR the two grants from the replicated
  // kill chain. We also AND in the global kin signal.

  assign grants
    = (grants_int[NUM_REQS-1:0] | grants_int[2*NUM_REQS-1:NUM_REQS])
    & {NUM_REQS{~kin}};

  assign kout = kills[2*NUM_REQS] || kin;

endmodule

//------------------------------------------------------------------------
// vc_VariableArb
//------------------------------------------------------------------------
// The input priority signal is a one-hot signal where the one indicates
// which request should be given highest priority.

module vc_VariableArb #( parameter NUM_REQS = 2 )
(
  input  [NUM_REQS-1:0] priority,  // (one-hot) 1 is req w/ highest pri
  input  [NUM_REQS-1:0] reqs,      // 1 = making a request, 0 = no request
  output [NUM_REQS-1:0] grants     // (one-hot) 1 is req won grant
);

  wire dummy_kout;

  vc_VariableArbChain#(NUM_REQS) variableArbChain
  (
    .kin      (1'b0),
    .priority (priority),
    .reqs     (reqs),
    .grants   (grants),
    .kout     (dummy_kout)
  );

endmodule

//------------------------------------------------------------------------
// vc_RoundRobinArbChain
//------------------------------------------------------------------------
// Ensures strong fairness among the requesters. The requester which wins
// the grant will be the lowest priority requester the next cycle.

module vc_RoundRobinArbChain
#(
  parameter NUM_REQS           = 2,
  parameter RESET_PRIORITY_VAL = 1  // (one-hot) 1 indicates which req
                                    //   has highest priority on reset
)(
  input                 clk,
  input                 reset,
  input                 kin,    // Kill in
  input  [NUM_REQS-1:0] reqs,   // 1 = making a request, 0 = no request
  output [NUM_REQS-1:0] grants, // (one-hot) 1 is req won grant
  output                kout    // Kill out
);

  // We only update the priority if a requester actually received a grant

  wire priority_en = |grants;

  // Next priority is just the one-hot grant vector left rotated by one

  wire [NUM_REQS-1:0] priority_next
    = { grants[NUM_REQS-2:0], grants[NUM_REQS-1] };

  // State for the one-hot priority vector

  wire [NUM_REQS-1:0] priority;

  vc_ERDFF_pf#(NUM_REQS,RESET_PRIORITY_VAL) priority_pf
  (
    .clk     (clk),
    .reset_p (reset),
    .en_p    (priority_en),
    .d_p     (priority_next),
    .q_np    (priority)
  );

  // Variable arbiter chain

  vc_VariableArbChain#(NUM_REQS) variableArbChain
  (
    .kin      (kin),
    .priority (priority),
    .reqs     (reqs),
    .grants   (grants),
    .kout     (kout)
  );

endmodule

//------------------------------------------------------------------------
// vc_RoundRobinArb
//------------------------------------------------------------------------
// Ensures strong fairness among the requesters. The requester which wins
// the grant will be the lowest priority requester the next cycle.
//
//  NOTE : Ideally we would just instantiate the vc_RoundRobinArbChain
//         and wire up kin to zero, but VCS seems to have trouble with
//         correctly elaborating the parameteres in that situation. So
//         for now we just duplicate the code from vc_RoundRobinArbChain
//

module vc_RoundRobinArb #( parameter NUM_REQS = 2 )
(
  input                 clk,
  input                 reset,
  input  [NUM_REQS-1:0] reqs,    // 1 = making a request, 0 = no request
  output [NUM_REQS-1:0] grants   // (one-hot) 1 is req won grant
);

  // We only update the priority if a requester actually received a grant
  wire priority_en = |grants;

  // Next priority is just the one-hot grant vector left rotated by one

  wire [NUM_REQS-1:0] priority_next
    = { grants[NUM_REQS-2:0], grants[NUM_REQS-1] };

  // State for the one-hot priority vector

  wire [NUM_REQS-1:0] priority;

  vc_ERDFF_pf#(NUM_REQS,1) priority_pf
  (
    .clk     (clk),
    .reset_p (reset),
    .en_p    (priority_en),
    .d_p     (priority_next),
    .q_np    (priority)
  );

  // Variable arbiter chain

  wire dummy_kout;

  vc_VariableArbChain#(NUM_REQS) variableArbChain
  (
    .kin      (1'b0),
    .priority (priority),
    .reqs     (reqs),
    .grants   (grants),
    .kout     (dummy_kout)
  );

  `ifndef SYNTHESIS
   `VC_ERRCHK_POSEDGE( clk, (priority_en != |grants),
                       "priority_en != |grants" );
  `endif

endmodule

`endif

