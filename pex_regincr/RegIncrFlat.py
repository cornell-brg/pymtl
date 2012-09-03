#=========================================================================
# RegIncrFlat
#=========================================================================
# This is a simple example of a model for a registered incrementer which
# combines a positive edge triggered register with a combinational +1
# incrementer. We use flat register-transfer-level modeling.

# Import the PyMTL framework

from pymtl import *

# Models must always inherit from the 'Model' base class

class RegIncrFlat( Model ):

  #-----------------------------------------------------------------------
  # Constructor
  #-----------------------------------------------------------------------
  # Declare the models port interface in the constructor along with any
  # internal wires which we need to communicate between concurrent blocks.

  def __init__( self ):

    # Instantiate input and output ports

    self.in_ = InPort  ( 16 )
    self.out = OutPort ( 16 )

    # Instantiate intermediate wires

    self.reg = Wire(16)

  #-----------------------------------------------------------------------
  # Register
  #-----------------------------------------------------------------------
  # We model sequential logic using the @posedge_clk decorator. This
  # logic will only happen once per cycle on the rising clock edge.
  # Within a posedge clk concurrent block we can read ports and wires
  # using .value, but we can only write ports and wires using .next
  # (never write a port or wire using .value within a posedge clk
  # concurrent block).

  @posedge_clk
  def register( self ):
    self.reg.next = self.in_.value

  #-----------------------------------------------------------------------
  # Incrementer
  #-----------------------------------------------------------------------
  # We model combinational logic using the @combinational decorator. This
  # logic will be re-evaluated every time and of the input ports or wires
  # change, and thus can potentially be evaluated multiple times in the
  # same cycle. Within a combinational concurrent block we can read and
  # write ports and wires using .value (never use .next within a
  # combinational concurrent block).

  @combinational
  def incrementer( self ):
    self.out.value = self.reg.value + 1

  #-----------------------------------------------------------------------
  # line_trace
  #-----------------------------------------------------------------------
  # If enabled in the simulator, a line trace will be printed every
  # cycle. If we print out the state at the beginning of the cycle and
  # what happened in the last cycle, this can be very useful for
  # debugging.

  def line_trace( self ):
    return "{:04x} ({:04x}) {:04x}" \
      .format( self.in_.value.uint, self.reg.value.uint, self.out.value.uint )

