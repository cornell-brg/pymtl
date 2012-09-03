#=========================================================================
# Connection Helpers Test Suite
#=========================================================================

from pymtl import *
from connects import *

#-------------------------------------------------------------------------
# Helper Model A
#-------------------------------------------------------------------------

class ModelA (Model):

  def __init__( self ):

    self.in_0  = InPort(1)
    self.in_1  = InPort(1)
    self.in_2  = InPort(1)
    self.in_3  = InPort(1)

    self.a2b_0 = OutPort(1)
    self.a2b_1 = OutPort(1)
    self.a2c_0 = OutPort(1)
    self.a2c_1 = OutPort(1)

    connect( self.in_0, self.a2b_0 )
    connect( self.in_1, self.a2b_1 )
    connect( self.in_2, self.a2c_0 )
    connect( self.in_3, self.a2c_1 )

#-------------------------------------------------------------------------
# Helper Model B
#-------------------------------------------------------------------------

class ModelB (Model):

  def __init__( self ):

    self.a2b_0 = InPort(1)
    self.a2b_1 = InPort(1)

    self.b2c_0 = OutPort(1)
    self.b2c_1 = OutPort(1)

    connect( self.a2b_0, self.b2c_0 )
    connect( self.a2b_1, self.b2c_1 )

#-------------------------------------------------------------------------
# Helper Model C
#-------------------------------------------------------------------------

class ModelC (Model):

  def __init__( self ):

    self.b2c_0 = InPort(1)
    self.b2c_1 = InPort(1)
    self.a2c_0 = InPort(1)
    self.a2c_1 = InPort(1)

    self.out_0 = OutPort(1)
    self.out_1 = OutPort(1)
    self.out_2 = OutPort(1)
    self.out_3 = OutPort(1)

    connect( self.b2c_0, self.out_0 )
    connect( self.b2c_1, self.out_1 )
    connect( self.a2c_0, self.out_2 )
    connect( self.a2c_1, self.out_3 )

#-------------------------------------------------------------------------
# TestHarnessAuto
#-------------------------------------------------------------------------

class TestHarnessAuto (Model):

  def __init__( self ):

    self.in_0  = InPort(1)
    self.in_1  = InPort(1)
    self.in_2  = InPort(1)
    self.in_3  = InPort(1)

    self.out_0 = OutPort(1)
    self.out_1 = OutPort(1)
    self.out_2 = OutPort(1)
    self.out_3 = OutPort(1)

    self.model_a = ModelA()
    self.model_b = ModelB()
    self.model_c = ModelC()

    connect_auto( self,         self.model_a )
    connect_auto( self.model_a, self.model_b )
    connect_auto( self.model_a, self.model_c )
    connect_auto( self.model_b, self.model_c )
    connect_auto( self.model_c, self         )

#-------------------------------------------------------------------------
# Test connect_auto
#-------------------------------------------------------------------------

def test_connect_auto( dump_vcd ):

  # Test vectors

  test_vectors = [
    # --- in ---  --- out ---
    # 0  1  2  3  0  1  2  3

    [ 0, 0, 0, 0, 0, 0, 0, 0 ],
    [ 0, 0, 0, 1, 0, 0, 0, 1 ],
    [ 0, 0, 1, 0, 0, 0, 1, 0 ],
    [ 0, 0, 1, 1, 0, 0, 1, 1 ],

    [ 0, 1, 0, 0, 0, 1, 0, 0 ],
    [ 0, 1, 0, 1, 0, 1, 0, 1 ],
    [ 0, 1, 1, 0, 0, 1, 1, 0 ],
    [ 0, 1, 1, 1, 0, 1, 1, 1 ],

    [ 1, 0, 0, 0, 1, 0, 0, 0 ],
    [ 1, 0, 0, 1, 1, 0, 0, 1 ],
    [ 1, 0, 1, 0, 1, 0, 1, 0 ],
    [ 1, 0, 1, 1, 1, 0, 1, 1 ],

    [ 1, 1, 0, 0, 1, 1, 0, 0 ],
    [ 1, 1, 0, 1, 1, 1, 0, 1 ],
    [ 1, 1, 1, 0, 1, 1, 1, 0 ],
    [ 1, 1, 1, 1, 1, 1, 1, 1 ],
  ]

  # Instantiate and elaborate the model

  model = TestHarnessAuto()
  model.elaborate()

  # Create a simulator using the simulation tool

  sim = SimulationTool( model )
  if dump_vcd:
    sim.dump_vcd( "pymtl-connects_test_connect_auto.vcd" )

  # Iterate setting the inputs and verifying the outputs each cycle

  print ""

  sim.reset()
  for test_vector in test_vectors:

    # Set inputs
    model.in_0.value = test_vector[0]
    model.in_1.value = test_vector[1]
    model.in_2.value = test_vector[2]
    model.in_3.value = test_vector[3]

    # Evaluate combinational concurrent blocks in simulator
    sim.eval_combinational()

    # Print the line trace
    sim.print_line_trace()

    # Verify outputs
    assert model.out_0.value == test_vector[4]
    assert model.out_1.value == test_vector[5]
    assert model.out_2.value == test_vector[6]
    assert model.out_3.value == test_vector[7]

    # Tick the simulator one cycle
    sim.cycle()

  # Add a couple extra ticks so that the VCD dump is nicer

  sim.cycle()
  sim.cycle()
  sim.cycle()

#-------------------------------------------------------------------------
# Helper Model D
#-------------------------------------------------------------------------

class ModelD (Model):

  def __init__( self ):

    self.in_0  = InPort(1)
    self.in_1  = InPort(1)
    self.in_2  = InPort(1)
    self.in_3  = InPort(1)

    self.out_a = OutPort(1)
    self.out_b = OutPort(1)
    self.out_c = OutPort(1)
    self.out_d = OutPort(1)

    connect( self.in_0, self.out_a )
    connect( self.in_1, self.out_b )
    connect( self.in_2, self.out_c )
    connect( self.in_3, self.out_d )

#-------------------------------------------------------------------------
# Helper Model E
#-------------------------------------------------------------------------

class ModelE (Model):

  def __init__( self ):

    self.in_a  = InPort(1)
    self.in_b  = InPort(1)
    self.in_c  = InPort(1)
    self.in_d  = InPort(1)

    self.out_0 = OutPort(1)
    self.out_1 = OutPort(1)
    self.out_2 = OutPort(1)
    self.out_3 = OutPort(1)

    connect( self.in_a, self.out_0 )
    connect( self.in_b, self.out_1 )
    connect( self.in_c, self.out_2 )
    connect( self.in_d, self.out_3 )

#-------------------------------------------------------------------------
# Helper Model F
#-------------------------------------------------------------------------

class ModelF (Model):

  def __init__( self ):

    self.in_0  = InPort(1)
    self.in_1  = InPort(1)
    self.in_2  = InPort(1)
    self.in_3  = InPort(1)

    self.out_0 = OutPort(1)
    self.out_1 = OutPort(1)
    self.out_2 = OutPort(1)
    self.out_3 = OutPort(1)

    connect( self.in_0, self.out_0 )
    connect( self.in_1, self.out_1 )
    connect( self.in_2, self.out_2 )
    connect( self.in_3, self.out_3 )

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarnessChain (Model):

  def __init__( self ):

    self.in_0  = InPort(1)
    self.in_1  = InPort(1)
    self.in_2  = InPort(1)
    self.in_3  = InPort(1)

    self.out_0 = OutPort(1)
    self.out_1 = OutPort(1)
    self.out_2 = OutPort(1)
    self.out_3 = OutPort(1)

    self.model_d = ModelD()
    self.model_e = ModelE()
    self.model_f = ModelF()

    # Connect input ports of the harness to beginning of chain
    connect_auto( self, self.model_d )

    # Connect chain together
    connect_chain([ self.model_d, self.model_e, self.model_f ])

    # Connect end of chain to output ports of the harness
    connect_auto( self, self.model_f )

#-------------------------------------------------------------------------
# Test connect_auto
#-------------------------------------------------------------------------

def test_connect_auto( dump_vcd ):

  # Test vectors

  test_vectors = [
    # --- in ---  --- out ---
    # 0  1  2  3  0  1  2  3

    [ 0, 0, 0, 0, 0, 0, 0, 0 ],
    [ 0, 0, 0, 1, 0, 0, 0, 1 ],
    [ 0, 0, 1, 0, 0, 0, 1, 0 ],
    [ 0, 0, 1, 1, 0, 0, 1, 1 ],

    [ 0, 1, 0, 0, 0, 1, 0, 0 ],
    [ 0, 1, 0, 1, 0, 1, 0, 1 ],
    [ 0, 1, 1, 0, 0, 1, 1, 0 ],
    [ 0, 1, 1, 1, 0, 1, 1, 1 ],

    [ 1, 0, 0, 0, 1, 0, 0, 0 ],
    [ 1, 0, 0, 1, 1, 0, 0, 1 ],
    [ 1, 0, 1, 0, 1, 0, 1, 0 ],
    [ 1, 0, 1, 1, 1, 0, 1, 1 ],

    [ 1, 1, 0, 0, 1, 1, 0, 0 ],
    [ 1, 1, 0, 1, 1, 1, 0, 1 ],
    [ 1, 1, 1, 0, 1, 1, 1, 0 ],
    [ 1, 1, 1, 1, 1, 1, 1, 1 ],
  ]

  # Instantiate and elaborate the model

  model = TestHarnessChain()
  model.elaborate()

  # Create a simulator using the simulation tool

  sim = SimulationTool( model )
  if dump_vcd:
    sim.dump_vcd( "pymtl-connects_test_connect_chain.vcd" )

  # Iterate setting the inputs and verifying the outputs each cycle

  print ""

  sim.reset()
  for test_vector in test_vectors:

    # Set inputs
    model.in_0.value = test_vector[0]
    model.in_1.value = test_vector[1]
    model.in_2.value = test_vector[2]
    model.in_3.value = test_vector[3]

    # Evaluate combinational concurrent blocks in simulator
    sim.eval_combinational()

    # Print the line trace
    sim.print_line_trace()

    # Verify outputs
    assert model.out_0.value == test_vector[4]
    assert model.out_1.value == test_vector[5]
    assert model.out_2.value == test_vector[6]
    assert model.out_3.value == test_vector[7]

    # Tick the simulator one cycle
    sim.cycle()

  # Add a couple extra ticks so that the VCD dump is nicer

  sim.cycle()
  sim.cycle()
  sim.cycle()

