#=========================================================================
# RoundRobinArbiter3x3
#=========================================================================

from   pymtl import *
import pmlib

from pmlib    import TestVectorSimulator

#-------------------------------------------------------------------------
# Round Robin Arbiter
#-------------------------------------------------------------------------

class RoundRobinArbiter3x3(Model):

  def __init__(s):

    s.nreqs        = 3

    # Interface Ports

    s.reqs         = InPort  (s.nreqs)
    s.grants       = OutPort (s.nreqs)

    # expand wires

    s.reqs0        = Wire( 1 )
    s.reqs1        = Wire( 1 )
    s.reqs2        = Wire( 1 )

    connect( s.reqs0, s.reqs[0] )
    connect( s.reqs1, s.reqs[1] )
    connect( s.reqs2, s.reqs[2] )

    s.grants0      = Wire( 1 )
    s.grants1      = Wire( 1 )
    s.grants2      = Wire( 1 )

    connect( s.grants0, s.grants[0] )
    connect( s.grants1, s.grants[1] )
    connect( s.grants2, s.grants[2] )

    # Temp Wires

    s.kills0       = Wire( 1 )
    s.kills1       = Wire( 1 )
    s.kills2       = Wire( 1 )
    s.kills3       = Wire( 1 )
    s.kills4       = Wire( 1 )
    s.kills5       = Wire( 1 )
    s.kills6       = Wire( 1 )

    s.priority_int0 = Wire( 1 )
    s.priority_int1 = Wire( 1 )
    s.priority_int2 = Wire( 1 )
    s.priority_int3 = Wire( 1 )
    s.priority_int4 = Wire( 1 )
    s.priority_int5 = Wire( 1 )

    s.reqs_int0     = Wire( 1 )
    s.reqs_int1     = Wire( 1 )
    s.reqs_int2     = Wire( 1 )
    s.reqs_int3     = Wire( 1 )
    s.reqs_int4     = Wire( 1 )
    s.reqs_int5     = Wire( 1 )

    s.grants_int0   = Wire( 1 )
    s.grants_int1   = Wire( 1 )
    s.grants_int2   = Wire( 1 )
    s.grants_int3   = Wire( 1 )
    s.grants_int4   = Wire( 1 )
    s.grants_int5   = Wire( 1 )

    # priority enable

    s.priority_en  = Wire( 1 )

    s.priority_out0 =  Wire( 1 )
    s.priority_out1 =  Wire( 1 )
    s.priority_out2 =  Wire( 1 )

    # priority register

    s.priority_reg = m = pmlib.regs.RegEnRst( s.nreqs,
                              reset_value = 1 )
    connect({
      m.en             : s.priority_en,
      m.in_[1:s.nreqs] : s.grants[0:s.nreqs-1],
      m.in_[0]         : s.grants[s.nreqs-1],
    })

    connect( s.priority_out0, s.priority_reg.out[0] )
    connect( s.priority_out1, s.priority_reg.out[1] )
    connect( s.priority_out2, s.priority_reg.out[2] )

  @combinational
  def comb(s):

    s.kills0.value         = 1

    s.priority_int0.value  = s.priority_out0.value
    s.priority_int1.value  = s.priority_out1.value
    s.priority_int2.value  = s.priority_out2.value
    s.priority_int3.value  = 0
    s.priority_int4.value  = 0
    s.priority_int5.value  = 0

    s.reqs_int0.value = s.reqs0.value
    s.reqs_int1.value = s.reqs1.value
    s.reqs_int2.value = s.reqs2.value
    s.reqs_int3.value = s.reqs0.value
    s.reqs_int4.value = s.reqs1.value
    s.reqs_int5.value = s.reqs2.value

    # expanded logic

    # 0
    if s.priority_int0.value:
      s.grants_int0.value = s.reqs_int0.value
    else:
      s.grants_int0.value = ~s.kills0.value & s.reqs_int0.value

    if s.priority_int0.value:
      s.kills1.value = s.grants_int0.value
    else:
      s.kills1.value = s.kills0.value | s.grants_int0.value

    # 1
    if s.priority_int1.value:
      s.grants_int1.value = s.reqs_int1.value
    else:
      s.grants_int1.value = ~s.kills1.value & s.reqs_int1.value

    if s.priority_int1.value:
      s.kills2.value = s.grants_int1.value
    else:
      s.kills2.value = s.kills1.value | s.grants_int1.value

    # 2
    if s.priority_int2.value:
      s.grants_int2.value = s.reqs_int2.value
    else:
      s.grants_int2.value = ~s.kills2.value & s.reqs_int2.value

    if s.priority_int2.value:
      s.kills3.value = s.grants_int2.value
    else:
      s.kills3.value = s.kills2.value | s.grants_int2.value

    # 3
    if s.priority_int3.value:
      s.grants_int3.value = s.reqs_int3.value
    else:
      s.grants_int3.value = ~s.kills3.value & s.reqs_int3.value

    if s.priority_int3.value:
      s.kills4.value = s.grants_int3.value
    else:
      s.kills4.value = s.kills3.value | s.grants_int3.value

    # 4
    if s.priority_int4.value:
      s.grants_int4.value = s.reqs_int4.value
    else:
      s.grants_int4.value = ~s.kills4.value & s.reqs_int4.value

    if s.priority_int4.value:
      s.kills5.value = s.grants_int4.value
    else:
      s.kills5.value = s.kills4.value | s.grants_int4.value

    # 5
    if s.priority_int5.value:
      s.grants_int5.value = s.reqs_int5.value
    else:
      s.grants_int5.value = ~s.kills5.value & s.reqs_int5.value

    if s.priority_int5.value:
      s.kills6.value = s.grants_int5.value
    else:
      s.kills6.value = s.kills5.value | s.grants_int5.value

    # grants logic

    #0
    s.grants0.value = s.grants_int0.value | s.grants_int3.value

    #1
    s.grants1.value = s.grants_int1.value | s.grants_int4.value

    #2
    s.grants2.value = s.grants_int2.value | s.grants_int5.value

    # priority enable
    s.priority_en.value = ( s.grants.value != 0 )

  def line_trace(s):
    return "{:03b} | {:03b}".format( s.reqs.value.uint, s.grants.value.uint )

#-------------------------------------------------------------------------
# Round Robin Aribter Tests
#-------------------------------------------------------------------------

# Test Harness

def run_test( dump_vcd, ModelType, test_vectors ):

  # Instantiate and elaborate the model

  model = ModelType( )
  model.elaborate()

  # Define functions mapping the test vector to ports in model

  def tv_in( model, test_vector ):
    model.reqs.value = test_vector[0]

  def tv_out( model, test_vector ):
    assert model.grants.value == test_vector[1]

  # Run the test

  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  if dump_vcd:
    sim.dump_vcd( "test_rr3_arb" + str(nreqs) + ".vcd" )
  sim.run_test()

#-------------------------------------------------------------------------
# Arbiter with Four Requesters
#-------------------------------------------------------------------------

def test_rr_arb_3( dump_vcd ):
  run_test( dump_vcd, RoundRobinArbiter3x3, [


    # reqs    grants
    [ 0b000,  0b000 ],

    [ 0b001,  0b001 ],
    [ 0b010,  0b010 ],
    [ 0b100,  0b100 ],

    [ 0b111,  0b001 ],
    [ 0b111,  0b010 ],
    [ 0b111,  0b100 ],
    [ 0b111,  0b001 ],

    [ 0b101,  0b100 ],
    [ 0b011,  0b001 ],
    [ 0b110,  0b010 ],
    [ 0b101,  0b100 ],
    [ 0b011,  0b001 ],
  ])


