#=========================================================================
# Connection Helpers Test Suite
#=========================================================================

from pymtl import *
from connects import *

from TestVectorSimulator import TestVectorSimulator

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
# TestHarness
#-------------------------------------------------------------------------

class TestHarness (Model):

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

    auto_connect( self,         self.model_a )
    auto_connect( self.model_a, self.model_b )
    auto_connect( self.model_a, self.model_c )
    auto_connect( self.model_b, self.model_c )
    auto_connect( self.model_c, self         )

#-------------------------------------------------------------------------
# Test basics
#-------------------------------------------------------------------------

def test_basics( dump_vcd ):

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

  model = TestHarness()
  model.elaborate()

  # Define functions mapping the test vector to ports in model

  def tv_in( model, test_vector ):
    model.in_0.value = test_vector[0]
    model.in_1.value = test_vector[1]
    model.in_2.value = test_vector[2]
    model.in_3.value = test_vector[3]

  def tv_out( model, test_vector ):
    assert model.out_0.value == test_vector[4]
    assert model.out_1.value == test_vector[5]
    assert model.out_2.value == test_vector[6]
    assert model.out_3.value == test_vector[7]

  # Run the test

  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  if dump_vcd:
    sim.dump_vcd( "pmlib-connects-test_basics.vcd" )
  sim.run_test()

