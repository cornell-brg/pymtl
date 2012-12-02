#=========================================================================
# RoundRobinArbiter5x5
#=========================================================================

from   pymtl import *
import pmlib

from pmlib    import TestVectorSimulator

#-------------------------------------------------------------------------
# Round Robin Arbiter
#-------------------------------------------------------------------------

class RoundRobinArbiter5x5(Model):

  def __init__(s):

    s.nreqs        = 5

    # Interface Ports

    s.reqs         = InPort  (s.nreqs)
    s.grants       = OutPort (s.nreqs)

    # expand wires

    s.reqs0        = Wire( 1 )
    s.reqs1        = Wire( 1 )
    s.reqs2        = Wire( 1 )
    s.reqs3        = Wire( 1 )
    s.reqs4        = Wire( 1 )

    connect( s.reqs0, s.reqs[0] )
    connect( s.reqs1, s.reqs[1] )
    connect( s.reqs2, s.reqs[2] )
    connect( s.reqs3, s.reqs[3] )
    connect( s.reqs4, s.reqs[4] )

    s.grants0      = Wire( 1 )
    s.grants1      = Wire( 1 )
    s.grants2      = Wire( 1 )
    s.grants3      = Wire( 1 )
    s.grants4      = Wire( 1 )

    connect( s.grants0, s.grants[0] )
    connect( s.grants1, s.grants[1] )
    connect( s.grants2, s.grants[2] )
    connect( s.grants3, s.grants[3] )
    connect( s.grants4, s.grants[4] )

    # Temp Wires

    s.kills0       = Wire( 1 )
    s.kills1       = Wire( 1 )
    s.kills2       = Wire( 1 )
    s.kills3       = Wire( 1 )
    s.kills4       = Wire( 1 )
    s.kills5       = Wire( 1 )
    s.kills6       = Wire( 1 )
    s.kills7       = Wire( 1 )
    s.kills8       = Wire( 1 )
    s.kills9       = Wire( 1 )
    s.kills10      = Wire( 1 )

    s.priority_int0 = Wire( 1 )
    s.priority_int1 = Wire( 1 )
    s.priority_int2 = Wire( 1 )
    s.priority_int3 = Wire( 1 )
    s.priority_int4 = Wire( 1 )
    s.priority_int5 = Wire( 1 )
    s.priority_int6 = Wire( 1 )
    s.priority_int7 = Wire( 1 )
    s.priority_int8 = Wire( 1 )
    s.priority_int9 = Wire( 1 )

    s.reqs_int0     = Wire( 1 )
    s.reqs_int1     = Wire( 1 )
    s.reqs_int2     = Wire( 1 )
    s.reqs_int3     = Wire( 1 )
    s.reqs_int4     = Wire( 1 )
    s.reqs_int5     = Wire( 1 )
    s.reqs_int6     = Wire( 1 )
    s.reqs_int7     = Wire( 1 )
    s.reqs_int8     = Wire( 1 )
    s.reqs_int9     = Wire( 1 )

    s.grants_int0   = Wire( 1 )
    s.grants_int1   = Wire( 1 )
    s.grants_int2   = Wire( 1 )
    s.grants_int3   = Wire( 1 )
    s.grants_int4   = Wire( 1 )
    s.grants_int5   = Wire( 1 )
    s.grants_int6   = Wire( 1 )
    s.grants_int7   = Wire( 1 )
    s.grants_int8   = Wire( 1 )
    s.grants_int9   = Wire( 1 )

    # priority enable

    s.priority_en  = Wire( 1 )

    s.priority_out0 =  Wire( 1 )
    s.priority_out1 =  Wire( 1 )
    s.priority_out2 =  Wire( 1 )
    s.priority_out3 =  Wire( 1 )
    s.priority_out4 =  Wire( 1 )

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
    connect( s.priority_out3, s.priority_reg.out[3] )
    connect( s.priority_out4, s.priority_reg.out[4] )

  @combinational
  def comb(s):

    s.kills0.value         = 1

    s.priority_int0.value  = s.priority_out0.value
    s.priority_int1.value  = s.priority_out1.value
    s.priority_int2.value  = s.priority_out2.value
    s.priority_int3.value  = s.priority_out3.value
    s.priority_int4.value  = s.priority_out4.value
    s.priority_int5.value  = 0
    s.priority_int6.value  = 0
    s.priority_int7.value  = 0
    s.priority_int8.value  = 0
    s.priority_int9.value  = 0

    s.reqs_int0.value = s.reqs0.value
    s.reqs_int1.value = s.reqs1.value
    s.reqs_int2.value = s.reqs2.value
    s.reqs_int3.value = s.reqs3.value
    s.reqs_int4.value = s.reqs4.value
    s.reqs_int5.value = s.reqs0.value
    s.reqs_int6.value = s.reqs1.value
    s.reqs_int7.value = s.reqs2.value
    s.reqs_int8.value = s.reqs3.value
    s.reqs_int9.value = s.reqs4.value

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

    # 6
    if s.priority_int6.value:
      s.grants_int6.value = s.reqs_int6.value
    else:
      s.grants_int6.value = ~s.kills6.value & s.reqs_int6.value

    if s.priority_int6.value:
      s.kills7.value = s.grants_int6.value
    else:
      s.kills7.value = s.kills6.value | s.grants_int6.value

    # 7
    if s.priority_int7.value:
      s.grants_int7.value = s.reqs_int7.value
    else:
      s.grants_int7.value = ~s.kills7.value & s.reqs_int7.value

    if s.priority_int7.value:
      s.kills8.value = s.grants_int7.value
    else:
      s.kills8.value = s.kills7.value | s.grants_int7.value

    # 8
    if s.priority_int8.value:
      s.grants_int8.value = s.reqs_int8.value
    else:
      s.grants_int8.value = ~s.kills8.value & s.reqs_int8.value

    if s.priority_int8.value:
      s.kills9.value = s.grants_int8.value
    else:
      s.kills9.value = s.kills8.value | s.grants_int8.value

    # 9
    if s.priority_int9.value:
      s.grants_int9.value = s.reqs_int9.value
    else:
      s.grants_int9.value = ~s.kills9.value & s.reqs_int9.value

    if s.priority_int9.value:
      s.kills10.value = s.grants_int9.value
    else:
      s.kills10.value = s.kills9.value | s.grants_int9.value

    # grants logic

    #0
    s.grants0.value = s.grants_int0.value | s.grants_int5.value

    #1
    s.grants1.value = s.grants_int1.value | s.grants_int6.value

    #2
    s.grants2.value = s.grants_int2.value | s.grants_int7.value

    #3
    s.grants3.value = s.grants_int3.value | s.grants_int8.value

    #4
    s.grants4.value = s.grants_int4.value | s.grants_int9.value

    # priority enable
    s.priority_en.value = ( s.grants.value != 0 )

  def line_trace(s):
    return "{:05b} | {:05b}".format( s.reqs.value.uint, s.grants.value.uint )

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
    sim.dump_vcd( "test_rr_arb" + str(nreqs) + ".vcd" )
  sim.run_test()

#-------------------------------------------------------------------------
# Arbiter with Four Requesters
#-------------------------------------------------------------------------

def test_rr_arb_5( dump_vcd ):
  run_test( dump_vcd, RoundRobinArbiter5x5, [


    # reqs      grants
    [ 0b00000,  0b00000 ],

    [ 0b00001,  0b00001 ],
    [ 0b00010,  0b00010 ],
    [ 0b00100,  0b00100 ],
    [ 0b01000,  0b01000 ],
    [ 0b10000,  0b10000 ],

    [ 0b11111,  0b00001 ],
    [ 0b11111,  0b00010 ],
    [ 0b11111,  0b00100 ],
    [ 0b11111,  0b01000 ],
    [ 0b11111,  0b10000 ],
    [ 0b11111,  0b00001 ],

    [ 0b11000,  0b01000 ],
    [ 0b10100,  0b10000 ],
    [ 0b10001,  0b00001 ],
    [ 0b00110,  0b00010 ],
    [ 0b00101,  0b00100 ],
    [ 0b00011,  0b00001 ],
  ])


