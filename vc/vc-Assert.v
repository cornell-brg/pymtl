//========================================================================
// vc-Assert
//========================================================================

`ifndef VC_ASSERT_V
`define VC_ASSERT_V

// Define a start time for when RTL assertion checking should begin.
// This avoids assertion checks which fail before the model is reset
// into a valid state.  Note, we assume a 10 ns clock period.
`define VC_ERROR_CHECK_START_TIME 10005

//------------------------------------------------------------------------
// Basic error macros
//------------------------------------------------------------------------

`define VC_ERROR(msg) \
  if ($time > `VC_ERROR_CHECK_START_TIME) \
    $display( " RTL-ERROR ( time = %d ) %m : %s", $time, msg )

`define VC_WARNING(msg) \
  if ($time > `VC_ERROR_CHECK_START_TIME) \
    $display( " RTL-WARNING ( time = %d ) %m : %s", $time, msg )

`define VC_ERROR_1ARG(msg, arg1) \
  if ($time > `VC_ERROR_CHECK_START_TIME) \
    $display( " RTL-ERROR ( time = %d ) %m : %s : 0x%0x", $time, msg, arg1 )

`define VC_ERROR_2ARG(msg, arg1, arg2) \
  if ($time > `VC_ERROR_CHECK_START_TIME) \
    $display( " RTL-ERROR ( time = %d ) %m : %s : 0x%0x 0x%0x", $time, msg, arg1, arg2 )

//------------------------------------------------------------------------
// Basic assert and error checking macros
//------------------------------------------------------------------------

`define VC_ASSERT(goodcond, msg) \
  if (goodcond); \
  else `VC_ERROR( ({"assertion failed : ", msg}) )

`define VC_ASSERT_1ARG(goodcond, msg, arg1) \
  if (goodcond); \
  else `VC_ERROR( ({"assertion failed : ",msg}), arg1 )

`define VC_ASSERT_2ARG(goodcond, msg, arg1, arg2) \
  if (goodcond); \
  else `VC_ERROR_2ARG( ({"assertion failed : ",msg}), arg1, arg2 )

`define VC_ASSERT_POSEDGE(clk, goodcond, msg) \
  always @(posedge clk) \
    `VC_ASSERT( goodcond, msg )

`define VC_ERRCHK(badcond, msg) \
  if (!(badcond)); \
  else `VC_ERROR( msg )

`define VC_ERRCHK_1ARG(badcond, msg, arg1) \
  if (!(badcond)); \
  else `VC_ERROR_1ARG( msg, arg1 )

`define VC_ERRCHK_2ARG(badcond, msg, arg1, arg2) \
  if (!(badcond)); \
  else `VC_ERROR_2ARG( msg, arg1, arg2 )

`define VC_ERRCHK_POSEDGE(clk, badcond, msg) \
  always @(posedge clk) \
    `VC_ERRCHK( badcond, msg )

`define VC_ERRCHK_NEGEDGE(clk, badcond, msg) \
  always @(negedge clk) \
    `VC_ERRCHK( badcond, msg )

//------------------------------------------------------------------------
// X handling macros
//------------------------------------------------------------------------

`define VC_PROPAGATE_X(i, o) \
  if ((|(i ^ i)) == 1'b0); \
  else o = o + 1'bx

`define VC_ASSERT_NOT_X_MSG(net, msg) \
  if ((|(net ^ net)) == 1'b0); \
  else `VC_ERROR( ({"x assertion failed : ",msg}) )

`define VC_ASSERT_NOT_X_ALWAYS_MSG(net, msg) \
  always @* \
    `VC_ASSERT_NOT_X_MSG(net, msg)

`define VC_ASSERT_NOT_X_POSEDGE_MSG(clk, net, msg) \
  always @(posedge clk) \
    `VC_ASSERT_NOT_X_MSG(net, msg)

`define VC_ASSERT_NOT_X_NEGEDGE_MSG(clk, net, msg) \
  always @(negedge clk) \
    `VC_ASSERT_NOT_X_MSG(net, msg)

`define VC_ASSERT_NOT_X(net) \
  `VC_ASSERT_NOT_X_MSG(net, "")

`define VC_ASSERT_NOT_X_ALWAYS(net) \
  `VC_ASSERT_NOT_X_ALWAYS_MSG(net, "")

`define VC_ASSERT_NOT_X_POSEDGE(clk, net) \
  `VC_ASSERT_NOT_X_POSEDGE_MSG(clk, net, "")

`define VC_ASSERT_NOT_X_NEGEDGE(clk, net) \
  `VC_ASSERT_NOT_X_NEGEDGE_MSG(clk, net, "")

//------------------------------------------------------------------------
// One-hot macros
//------------------------------------------------------------------------

`define VC_IS_1HOT( net ) \
  ( |net && (((net-1) & net) == 1'b0) )

`define VC_ASSERT_1HOT_MSG( net, msg ) \
  if ( `VC_IS_1HOT( net ) ); \
  else `VC_ERROR_1ARG( ({"one hot assertion failed : ",msg}), net )

`define VC_ASSERT_1HOT_ALWAYS_MSG( net, msg ) \
  always @(*) \
    `VC_ASSERT_1HOT_MSG( net, msg )

`define VC_ASSERT_1HOT_POSEDGE_MSG( clk, net, msg ) \
  always @( posedge clk ) \
    `VC_ASSERT_1HOT_MSG( net, msg )

`define VC_ASSERT_1HOT_NEGEDGE_MSG( clk, net, msg ) \
  always @( negedge clk ) \
    `VC_ASSERT_1HOT_MSG( net, msg )

`define VC_ASSERT_1HOT( net ) \
  if ( `VC_IS_1HOT( net ) ); \
  else `VC_ERROR_1ARG( ({"one hot assertion failed"}), net )

`define VC_ASSERT_1HOT_ALWAYS( net ) \
  always @(*) \
    `VC_ASSERT_1HOT_MSG( net, "" )

`define VC_ASSERT_1HOT_POSEDGE( clk, net ) \
  always @( posedge clk ) \
    `VC_ASSERT_1HOT_MSG( net, "" )

`define VC_ASSERT_1HOT_NEGEDGE( clk, net ) \
  always @( negedge clk ) \
    `VC_ASSERT_1HOT_MSG( net, "" )

//------------------------------------------------------------------------
// One-hot or zero macros
//------------------------------------------------------------------------

`define VC_IS_1HOT_OR_ZERO( net ) \
  ( ((net-1) & net) == 1'b0 )

`define VC_ASSERT_1HOT_OR_ZERO_MSG( net, msg ) \
  if ( `VC_IS_1HOT_OR_ZERO( net ) ); \
  else `VC_ERROR_1ARG( ({"one hot or zero assertion failed : ",msg}), net )

`define VC_ASSERT_1HOT_OR_ZERO_ALWAYS_MSG( net, msg ) \
  always @(*) \
    `VC_ASSERT_1HOT_OR_ZERO_MSG( net, msg )

`define VC_ASSERT_1HOT_OR_ZERO_POSEDGE_MSG( clk, net, msg ) \
  always @( posedge clk ) \
    `VC_ASSERT_1HOT_OR_ZERO_MSG( net, msg )

`define VC_ASSERT_1HOT_OR_ZERO_NEGEDGE_MSG( clk, net, msg ) \
  always @( negedge clk ) \
    `VC_ASSERT_1HOT_OR_ZERO_MSG( net, msg )

`define VC_ASSERT_1HOT_OR_ZERO( net ) \
  if ( `VC_IS_1HOT_OR_ZERO( net ) ); \
  else `VC_ERROR_1ARG( ({"one hot or zero assertion failed"}), net )

`define VC_ASSERT_1HOT_OR_ZERO_ALWAYS( net ) \
  always @(*) \
    `VC_ASSERT_1HOT_OR_ZERO_MSG( net, "" )

`define VC_ASSERT_1HOT_OR_ZERO_POSEDGE( clk, net ) \
  always @( posedge clk ) \
    `VC_ASSERT_1HOT_OR_ZERO_MSG( net, "" )

`define VC_ASSERT_1HOT_OR_ZERO_NEGEDGE( clk, net ) \
  always @( negedge clk ) \
    `VC_ASSERT_1HOT_OR_ZERO_MSG( net, "" )

`endif

