//========================================================================
// Verilog Components: Queues
//========================================================================

`ifndef VC_QUEUES_V
`define VC_QUEUES_V

`include "vc-Misc.v"
`include "vc-StateElements.v"
`include "vc-Muxes.v"
`include "vc-Regfiles.v"

//------------------------------------------------------------------------
// Defines
//------------------------------------------------------------------------

`define VC_QUEUE_NORMAL   4'b0000
`define VC_QUEUE_PIPE     4'b0001
`define VC_QUEUE_BYPASS   4'b0010
`define VC_QUEUE_SKID     4'b0100

//------------------------------------------------------------------------
// Single-Element Queue Control Logic
//------------------------------------------------------------------------
// This is the control logic for a single-elment queue. It is designed to
// be attached to a storage element with a write enable. Additionally, it
// includes the ability to statically enable pipeline and/or bypass
// behavior. Pipeline behavior is when the deq_rdy signal is
// combinationally wired to the enq_rdy signal allowing elements to be
// dequeued and enqueued in the same cycle when the queue is full. Bypass
// behavior is when the enq_val signal is combinationally wired to the
// deq_val signal allowing elements to bypass the storage element if the
// storage element is empty.

module vc_QueueCtrl1#( parameter TYPE = `VC_QUEUE_NORMAL )
(
  input  clk, reset,
  input  enq_val,        // Enqueue data is valid
  output enq_rdy,        // Ready for producer to do an enqueue
  output deq_val,        // Dequeue data is valid
  input  deq_rdy,        // Consumer is ready to do a dequeue
  output wen,            // Write en signal to wire up to storage element
  output bypass_mux_sel  // Used to control bypass mux for bypass queues
);

  // Status register

  reg  full;
  wire full_next;

  //vc_RDFF_pf#(1) full_pf
  //(
  //  .clk     (clk),
  //  .reset_p (reset),
  //  .d_p     (full_next),
  //  .q_np    (full)
  //);

  always @ (posedge clk) begin
    full <= reset ? 0 : full_next;
  end

  //always @ (negedge reset) begin
  //  full <= full_next;
  //end

  // Determine if pipeline or bypass behavior is enabled

  localparam PIPE_EN   = |( TYPE & `VC_QUEUE_PIPE   );
  localparam BYPASS_EN = |( TYPE & `VC_QUEUE_BYPASS );

  // We enq/deq only when they are both ready and valid

  wire do_enq = enq_rdy && enq_val;
  wire do_deq = deq_rdy && deq_val;

  // Determine if we have pipeline or bypass behaviour and
  // set the write enable accordingly.

  wire   empty     = ~full;
  wire   do_pipe   = PIPE_EN   && full  && do_enq && do_deq;
  wire   do_bypass = BYPASS_EN && empty && do_enq && do_deq;

  assign wen = do_enq && ~do_bypass;

  // Regardless of the type of queue or whether or not we are actually
  // doing a bypass, if the queue is empty then we select the enq
  // bits, otherwise we select the output of the queue state elements.

  assign bypass_mux_sel = empty;

  // Ready signals are calculated from full register. If pipeline
  // behavior is enabled, then the enq_rdy signal is also calculated
  // combinationally from the deq_rdy signal. If bypass behavior is
  // enabled then the deq_val signal is also calculated combinationally
  // from the enq_val signal.

  assign enq_rdy  = ~full  || ( PIPE_EN   && full  && deq_rdy );
  assign deq_val  = ~empty || ( BYPASS_EN && empty && enq_val );

  // Control logic for the full register input

  assign full_next = ( do_deq && ~do_pipe )   ? 1'b0
                   : ( do_enq && ~do_bypass ) ? 1'b1
                   :                            full;

  //`ifndef SYNTHESIS
  //  `VC_ASSERT_NOT_X_POSEDGE_MSG( clk, enq_val, "enq_val" );
  //  `VC_ASSERT_NOT_X_POSEDGE_MSG( clk, deq_rdy, "deq_rdy" );
  //`endif

endmodule

//------------------------------------------------------------------------
// Single-Element Queue Datapath (DFF-pf based)
//------------------------------------------------------------------------
// This is the datpath for single element queues. It includes a register
// and a bypass mux if needed.

module vc_QueueDpath1_pf
#(
  parameter TYPE    = `VC_QUEUE_NORMAL,
  parameter DATA_SZ = 1
)(
  input                clk,
  input                wen,
  input                bypass_mux_sel,
  input  [DATA_SZ-1:0] enq_bits,
  output [DATA_SZ-1:0] deq_bits
);

  // Queue storage

  wire [DATA_SZ-1:0] qstore_out;

  vc_EDFF_pf#(DATA_SZ) qstore
  (
    .clk  (clk),
    .en_p (wen),
    .d_p  (enq_bits),
    .q_np (qstore_out)
  );

  // Bypass muxing

  generate
  if ( |(TYPE & `VC_QUEUE_BYPASS ) )

    vc_Mux2#(DATA_SZ) bypass_mux
    (
      .in0 (qstore_out),
      .in1 (enq_bits),
      .sel (bypass_mux_sel),
      .out (deq_bits)
    );

  else
    assign deq_bits = qstore_out;
  endgenerate

endmodule

//------------------------------------------------------------------------
// Multi-Element Queue Control Logic
//------------------------------------------------------------------------
// This is the control logic for a multi-elment queue. It is designed to
// be attached to a Regfile storage element. Additionally, it includes
// the ability to statically enable pipeline and/or bypass behavior.
// Pipeline behavior is when the deq_rdy signal is combinationally wired
// to the enq_rdy signal allowing elements to be dequeued and enqueued in
// the same cycle when the queue is full. Bypass behavior is when the
// enq_val signal is cominationally wired to the deq_val signal allowing
// elements to bypass the storage element if the storage element is
// empty.

module vc_QueueCtrl
#(
  parameter TYPE    = `VC_QUEUE_NORMAL,
  parameter ENTRIES = 2,
  parameter ADDR_SZ = 1
)(
  input                clk, reset,
  input                enq_val,          // Enqueue data is valid
  output               enq_rdy,          // Ready for producer to enqueue
  output               deq_val,          // Dequeue data is valid
  input                deq_rdy,          // Consumer is ready to dequeue
  output               wen,              // Wen signal to wire to regfile
  output [ADDR_SZ-1:0] waddr,            // Write addr to wire to regfile
  output [ADDR_SZ-1:0] raddr,            // Read addr to wire to regfile
  output               bypass_mux_sel,   // Control mux for bypass queues
  output [ADDR_SZ:0]   num_free_entries  // Num of free entries in queue
);

  // Enqueue and dequeue pointers

  wire [ADDR_SZ-1:0] enq_ptr;
  wire [ADDR_SZ-1:0] enq_ptr_next;

  vc_RDFF_pf#(ADDR_SZ) enq_ptr_pf
  (
    .clk     (clk),
    .reset_p (reset),
    .d_p     (enq_ptr_next),
    .q_np    (enq_ptr)
  );

  wire [ADDR_SZ-1:0] deq_ptr;
  wire [ADDR_SZ-1:0] deq_ptr_next;

  vc_RDFF_pf#(ADDR_SZ) deq_ptr_pf
  (
    .clk     (clk),
    .reset_p (reset),
    .d_p     (deq_ptr_next),
    .q_np    (deq_ptr)
  );

  assign waddr = enq_ptr;
  assign raddr = deq_ptr;

  // Extra state to tell difference between full and empty

  wire full;
  wire full_next;

  vc_RDFF_pf#(1) full_pf
  (
    .clk     (clk),
    .reset_p (reset),
    .d_p     (full_next),
    .q_np    (full)
  );

  // Determine if pipeline or bypass behavior is enabled

  localparam PIPE_EN   = |( TYPE & `VC_QUEUE_PIPE   );
  localparam BYPASS_EN = |( TYPE & `VC_QUEUE_BYPASS );

  // We enq/deq only when they are both ready and valid

  wire do_enq = enq_rdy && enq_val;
  wire do_deq = deq_rdy && deq_val;

  // Determine if we have pipeline or bypass behaviour and
  // set the write enable accordingly.

  wire   empty     = ~full && (enq_ptr == deq_ptr);
  wire   do_pipe   = PIPE_EN   && full  && do_enq && do_deq;
  wire   do_bypass = BYPASS_EN && empty && do_enq && do_deq;

  assign wen = do_enq && ~do_bypass;

  // Regardless of the type of queue or whether or not we are actually
  // doing a bypass, if the queue is empty then we select the enq bits,
  // otherwise we select the output of the queue state elements.

  assign bypass_mux_sel = empty;

  // Ready signals are calculated from full register. If pipeline
  // behavior is enabled, then the enq_rdy signal is also calculated
  // combinationally from the deq_rdy signal. If bypass behavior is
  // enabled then the deq_val signal is also calculated combinationally
  // from the enq_val signal.

  assign enq_rdy  = ~full  || ( PIPE_EN   && full  && deq_rdy );
  assign deq_val  = ~empty || ( BYPASS_EN && empty && enq_val );

  // Control logic for the enq/deq pointers and full register

  wire [ADDR_SZ-1:0] deq_ptr_plus1 = deq_ptr + 1'b1;
  wire [ADDR_SZ-1:0] deq_ptr_inc
    = (deq_ptr_plus1 == ENTRIES) ? {ADDR_SZ{1'b0}} : deq_ptr_plus1;

  wire [ADDR_SZ-1:0] enq_ptr_plus1 = enq_ptr + 1'b1;
  wire [ADDR_SZ-1:0] enq_ptr_inc
    = (enq_ptr_plus1 == ENTRIES) ? {ADDR_SZ{1'b0}} : enq_ptr_plus1;

  assign deq_ptr_next
    = ( do_deq && ~do_bypass ) ? ( deq_ptr_inc ) : deq_ptr;

  assign enq_ptr_next
    = ( do_enq && ~do_bypass ) ? ( enq_ptr_inc ) : enq_ptr;

  assign full_next
    = ( do_enq && ~do_deq && ( enq_ptr_inc == deq_ptr ) ) ? 1'b1
    : ( do_deq && full && ~do_pipe )                      ? 1'b0
    :                                                       full;

  // Number of free entries

  generate
  if ( |( TYPE & `VC_QUEUE_SKID ) )
    assign num_free_entries
      = full                ? {(ADDR_SZ+1){1'b0}}
      : empty               ? ENTRIES[ADDR_SZ:0]
      : (enq_ptr > deq_ptr) ? ENTRIES[ADDR_SZ:0] - (enq_ptr - deq_ptr)
      : (deq_ptr > enq_ptr) ? deq_ptr - enq_ptr
      :                       {(ADDR_SZ+1){1'bx}};
  else
    assign num_free_entries = {ADDR_SZ{1'bx}};
  endgenerate

  // Trace State and Assertions

`ifndef SYNTHESIS
  reg [ADDR_SZ:0] entries;
  always @( posedge clk )
  begin

    if ( reset )
      entries <= 0;

    else if ( do_enq && ~do_deq && ~do_bypass && ~do_pipe )
      entries <= entries + 1;

    else if ( do_deq && ~do_enq && ~do_bypass && ~do_pipe )
      entries <= entries - 1;

    `VC_ASSERT_2ARG( entries <= ENTRIES,
                     "entries <= ENTRIES", entries, ENTRIES );

    `VC_ASSERT_2ARG( ENTRIES <= (1 << ADDR_SZ),
                     "ENTRIES <= ADDR_SZ", ENTRIES, ADDR_SZ );

    `VC_ASSERT_NOT_X_MSG( enq_val, "enq_val" );
    `VC_ASSERT_NOT_X_MSG( deq_rdy, "deq_rdy" );
  end
`endif

endmodule

//------------------------------------------------------------------------
// Multi-Element Queue Datapath (DFF-pf based)
//------------------------------------------------------------------------
// This is the datpath for multi-element queues. It includes a register
// and a bypass mux if needed.

module vc_QueueDpath_pf
#(
  parameter TYPE    = `VC_QUEUE_NORMAL,
  parameter DATA_SZ = 4,
  parameter ENTRIES = 2,
  parameter ADDR_SZ = 1
)(
  input                clk,
  input                wen,
  input                bypass_mux_sel,
  input  [ADDR_SZ-1:0] waddr,
  input  [ADDR_SZ-1:0] raddr,
  input  [DATA_SZ-1:0] enq_bits,
  output [DATA_SZ-1:0] deq_bits
);

  // Queue storage

  wire [DATA_SZ-1:0] qstore_out;

  vc_Regfile_1w1r_pf#(DATA_SZ,ENTRIES,ADDR_SZ) qstore
  (
    .clk     (clk),
    .wen_p   (wen),
    .waddr_p (waddr),
    .wdata_p (enq_bits),
    .raddr   (raddr),
    .rdata   (qstore_out)
  );

  // Bypass muxing

  generate
  if ( |(TYPE & `VC_QUEUE_BYPASS ) )

    vc_Mux2#(DATA_SZ) bypass_mux
    (
      .in0 (qstore_out),
      .in1 (enq_bits),
      .sel (bypass_mux_sel),
      .out (deq_bits)
    );

  else
    assign deq_bits = qstore_out;
  endgenerate

endmodule

//------------------------------------------------------------------------
// Queue (DFF-pf based)
//------------------------------------------------------------------------

module vc_Queue_pf
#(
  parameter TYPE    = `VC_QUEUE_NORMAL,
  parameter DATA_SZ = 1,
  parameter ENTRIES = 2,
  parameter ADDR_SZ = 1
)(
  input                clk,
  input                reset,
  input  [DATA_SZ-1:0] enq_bits,
  input                enq_val,
  output               enq_rdy,
  output [DATA_SZ-1:0] deq_bits,
  output               deq_val,
  input                deq_rdy
);

  generate
  if ( ENTRIES == 1 )
  begin

    wire wen;
    wire bypass_mux_sel;

    vc_QueueCtrl1#(TYPE) ctrl
    (
      .clk            (clk),
      .reset          (reset),
      .enq_val        (enq_val),
      .enq_rdy        (enq_rdy),
      .deq_val        (deq_val),
      .deq_rdy        (deq_rdy),
      .wen            (wen),
      .bypass_mux_sel (bypass_mux_sel)
    );

    vc_QueueDpath1_pf#(TYPE,DATA_SZ) dpath
    (
      .clk            (clk),
      .wen            (wen),
      .bypass_mux_sel (bypass_mux_sel),
      .enq_bits       (enq_bits),
      .deq_bits       (deq_bits)
    );

  end
  else
  begin: gen_q

    wire               wen;
    wire               bypass_mux_sel;
    wire [ADDR_SZ-1:0] waddr;
    wire [ADDR_SZ-1:0] raddr;
    wire [ADDR_SZ:0]   num_free_entries;

    vc_QueueCtrl#(TYPE,ENTRIES,ADDR_SZ) ctrl
    (
      .clk              (clk),
      .reset            (reset),
      .enq_val          (enq_val),
      .enq_rdy          (enq_rdy),
      .deq_val          (deq_val),
      .deq_rdy          (deq_rdy),
      .wen              (wen),
      .waddr            (waddr),
      .raddr            (raddr),
      .bypass_mux_sel   (bypass_mux_sel),
      .num_free_entries (num_free_entries)
    );

    vc_QueueDpath_pf#(TYPE,DATA_SZ,ENTRIES,ADDR_SZ) dpath
    (
      .clk            (clk),
      .wen            (wen),
      .bypass_mux_sel (bypass_mux_sel),
      .waddr          (waddr),
      .raddr          (raddr),
      .enq_bits       (enq_bits),
      .deq_bits       (deq_bits)
    );

  end
  endgenerate

endmodule

//------------------------------------------------------------------------
// Skid Queue (DFF-pf based)
//------------------------------------------------------------------------
// This queue includes an output port indicating how many free entries
// are left in the queue. We can use this when a queue is at the end of a
// pipeline and we can only stall the front of the pipeline. We need to
// stall the pipe when (num free entries <= num pipe stages).

module vc_SkidQueue_pf
#(
  parameter TYPE    = `VC_QUEUE_NORMAL,
  parameter DATA_SZ = 1,
  parameter ENTRIES = 2,
  parameter ADDR_SZ = 1
)(
  input                clk,
  input                reset,
  input  [DATA_SZ-1:0] enq_bits,
  input                enq_val,
  output               enq_rdy,
  output [DATA_SZ-1:0] deq_bits,
  output               deq_val,
  input                deq_rdy,
  output [ADDR_SZ:0]   num_free_entries
);

  wire               wen;
  wire               bypass_mux_sel;
  wire [ADDR_SZ-1:0] waddr;
  wire [ADDR_SZ-1:0] raddr;

  vc_QueueCtrl#((TYPE|`VC_QUEUE_SKID),ENTRIES,ADDR_SZ) ctrl
  (
    .clk              (clk),
    .reset            (reset),
    .enq_val          (enq_val),
    .enq_rdy          (enq_rdy),
    .deq_val          (deq_val),
    .deq_rdy          (deq_rdy),
    .wen              (wen),
    .waddr            (waddr),
    .raddr            (raddr),
    .bypass_mux_sel   (bypass_mux_sel),
    .num_free_entries (num_free_entries)
  );

  vc_QueueDpath_pf#((TYPE|`VC_QUEUE_SKID),DATA_SZ,ENTRIES,ADDR_SZ) dpath
  (
    .clk            (clk),
    .wen            (wen),
    .bypass_mux_sel (bypass_mux_sel),
    .waddr          (waddr),
    .raddr          (raddr),
    .enq_bits       (enq_bits),
    .deq_bits       (deq_bits)
  );

  `ifndef SYNTHESIS
    `VC_ASSERT_POSEDGE( clk, ENTRIES > 1, "ENTRIES > 1" );
  `endif

endmodule

//------------------------------------------------------------------------
// Delay Skid Queue (DFF-pf based)
//------------------------------------------------------------------------
// This queue inserts a statically defined delay between when items are
// enqueued and when they can be dequeued. This can be useful for
// testing. The delay must be less than 256. If the type includes the
// `VC_QUEUE_RANDOM flag then the delay is actually a random number of
// cycles not to exceed the DELAY parameter.
//
// Note that the queue is actually implemented with two queues: an input
// queue which has the type/entries given as parameters to the
// DelaySkidQueue and an output queue which is always a one element
// bypass queue. This means there is one extra slot of buffering - so if
// you set ENTRIES to 2 and the output is blocked forever, then the
// DelaySkidQueue can actually hold three elements (two in the inputQ and
// one in the outputQ).

module vc_DelaySkidQueue_pf
#(
  parameter DELAY    = 1,
  parameter TYPE     = `VC_QUEUE_NORMAL,
  parameter DATA_SZ  = 1,
  parameter ENTRIES  = 2,
  parameter ADDR_SZ  = 1
)(
  input                clk,
  input                reset,
  input  [DATA_SZ-1:0] enq_bits,
  input                enq_val,
  output               enq_rdy,
  output [DATA_SZ-1:0] deq_bits,
  output               deq_val,
  input                deq_rdy,
  output [ADDR_SZ:0]   num_free_entries
);

  // InputQ

  wire [DATA_SZ-1:0] inputQ_deq_bits;
  wire               inputQ_deq_val;
  wire               inputQ_deq_rdy;

  vc_SkidQueue_pf#(TYPE,DATA_SZ,ENTRIES,ADDR_SZ) inputQ
  (
    .clk              (clk),
    .reset            (reset),
    .enq_bits         (enq_bits),
    .enq_val          (enq_val),
    .enq_rdy          (enq_rdy),
    .deq_bits         (inputQ_deq_bits),
    .deq_val          (inputQ_deq_val),
    .deq_rdy          (inputQ_deq_rdy),
    .num_free_entries (num_free_entries)
  );

  // Delay counter

  localparam COUNTER_SZ = 8;

  wire [COUNTER_SZ-1:0] init_count;
  wire                  init_count_val;
  wire                  increment;
  wire                  decrement;
  wire [COUNTER_SZ-1:0] count_next;
  wire [COUNTER_SZ-1:0] count;

  vc_Counter_pf#(COUNTER_SZ,0) counter
  (
    .clk              (clk),
    .reset_p          (reset),
    .init_count_val_p (init_count_val),
    .init_count_p     (init_count),
    .increment_p      (increment),
    .decrement_p      (decrement),
    .count_next       (count_next),
    .count_np         (count)
  );

  // OutputQ

  wire [DATA_SZ-1:0] outputQ_enq_bits = inputQ_deq_bits;
  wire               outputQ_enq_val;
  wire               outputQ_enq_rdy;

  vc_Queue_pf#(`VC_QUEUE_BYPASS,DATA_SZ,1) outputQ
  (
    .clk              (clk),
    .reset            (reset),
    .enq_bits         (outputQ_enq_bits),
    .enq_val          (outputQ_enq_val),
    .enq_rdy          (outputQ_enq_rdy),
    .deq_bits         (deq_bits),
    .deq_val          (deq_val),
    .deq_rdy          (deq_rdy)
  );

  // Logic

  localparam [COUNTER_SZ-1:0] DELAY_SIZED = DELAY;
  localparam [COUNTER_SZ-1:0] CONST0 = 0;
  localparam [COUNTER_SZ-1:0] CONST1 = 1;

  assign init_count      = DELAY_SIZED;
  assign init_count_val  = (count == CONST0) && inputQ_deq_val;
  assign increment       = 1'b0;
  assign decrement       = (count != CONST0) && outputQ_enq_rdy;
  assign inputQ_deq_rdy  = (count == CONST1) && outputQ_enq_rdy;
  assign outputQ_enq_val = (count == CONST1) && outputQ_enq_rdy;

endmodule

//------------------------------------------------------------------------
// Random Delay Skid Queue (DFF-pf based)
//------------------------------------------------------------------------
// This queue inserts a random delay between when items are enqueued and
// when the can be dequeued. The maximum delay is specified statically as
// a parameter. See DelaySkidQueue for info on buffering ...

module vc_RandomDelaySkidQueue_pf
#(
  parameter MAX_DELAY = 1,
  parameter RAND_SEED = 32'hB9B9B9B9,
  parameter TYPE      = `VC_QUEUE_NORMAL,
  parameter DATA_SZ   = 1,
  parameter ENTRIES   = 2,
  parameter ADDR_SZ   = 1
)(
  input                clk,
  input                reset,
  input  [DATA_SZ-1:0] enq_bits,
  input                enq_val,
  output               enq_rdy,
  output [DATA_SZ-1:0] deq_bits,
  output               deq_val,
  input                deq_rdy,
  output [ADDR_SZ:0]   num_free_entries
);

  // InputQ

  wire [DATA_SZ-1:0] inputQ_deq_bits;
  wire               inputQ_deq_val;
  wire               inputQ_deq_rdy;

  vc_SkidQueue_pf#(TYPE,DATA_SZ,ENTRIES,ADDR_SZ) inputQ
  (
    .clk              (clk),
    .reset            (reset),
    .enq_bits         (enq_bits),
    .enq_val          (enq_val),
    .enq_rdy          (enq_rdy),
    .deq_bits         (inputQ_deq_bits),
    .deq_val          (inputQ_deq_val),
    .deq_rdy          (inputQ_deq_rdy),
    .num_free_entries (num_free_entries)
  );

  // Delay counter

  localparam COUNTER_SZ = 8;

  wire [COUNTER_SZ-1:0] init_count;
  wire                  init_count_val;
  wire                  increment;
  wire                  decrement;
  wire [COUNTER_SZ-1:0] count_next;
  wire [COUNTER_SZ-1:0] count;

  vc_Counter_pf#(COUNTER_SZ,0) counter
  (
    .clk              (clk),
    .reset_p          (reset),
    .init_count_val_p (init_count_val),
    .init_count_p     (init_count),
    .increment_p      (increment),
    .decrement_p      (decrement),
    .count_next       (count_next),
    .count_np         (count)
  );

  // Random number generator

  wire                  rng_next;
  wire [COUNTER_SZ-1:0] rng_out;

  vc_RandomNumberGenerator#(COUNTER_SZ,RAND_SEED) rng
  (
    .clk     (clk),
    .reset_p (reset),
    .next_p  (rng_next),
    .out_np  (rng_out)
  );

  // OutputQ

  wire [DATA_SZ-1:0] outputQ_enq_bits = inputQ_deq_bits;
  wire               outputQ_enq_val;
  wire               outputQ_enq_rdy;

  vc_Queue_pf#(`VC_QUEUE_BYPASS,DATA_SZ,1) outputQ
  (
    .clk              (clk),
    .reset            (reset),
    .enq_bits         (outputQ_enq_bits),
    .enq_val          (outputQ_enq_val),
    .enq_rdy          (outputQ_enq_rdy),
    .deq_bits         (deq_bits),
    .deq_val          (deq_val),
    .deq_rdy          (deq_rdy)
  );

  // Logic

  localparam [COUNTER_SZ-1:0] MAX_DELAY_SIZED = MAX_DELAY;
  localparam [COUNTER_SZ-1:0] CONST0 = 0;
  localparam [COUNTER_SZ-1:0] CONST1 = 1;

  assign rng_next        = (count == CONST0) && inputQ_deq_val;
  assign init_count      = ((rng_out % MAX_DELAY_SIZED)+CONST1);
  assign init_count_val  = (count == CONST0) && inputQ_deq_val;
  assign increment       = 1'b0;
  assign decrement       = (count != CONST0) && outputQ_enq_rdy;
  assign inputQ_deq_rdy  = (count == CONST1) && outputQ_enq_rdy;
  assign outputQ_enq_val = (count == CONST1) && outputQ_enq_rdy;

endmodule

`endif

