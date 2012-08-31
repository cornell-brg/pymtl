#=========================================================================
# Unit Tests for Registers
#=========================================================================

from regs import *
import random

#-------------------------------------------------------------------------
# Simple Register unit tests
#-------------------------------------------------------------------------

def test_Reg():

  model = Reg( 32 )
  model.elaborate()

  sim = SimulationTool( model )
  #sim.dump_vcd( "Reg_test.vcd" )

  sim.reset()
  test_cases = [ 0, 12, 17, 42, 1024, 9001, 0x7fffffff ]
  random_tests = [ random.randint( 0, 0x7fffffff ) for x in range( 20 ) ]
  test_cases.extend( random_tests )

  for i,value in enumerate( test_cases[1:] ):
    model.in_.value = value
    assert model.out.value == test_cases[i]
    sim.cycle()
    assert model.out.value == value

  #hdl = VerilogTranslationTool( model )
  #hdl.translate( "Reg.v" )

#-------------------------------------------------------------------------
# Register with Reset unit test
#-------------------------------------------------------------------------

def test_RegRst():

  model = RegRst( 32 )
  model.elaborate()

  sim = SimulationTool( model )
  #sim.dump_vcd( "RegRst_test.vcd" )

  sim.reset()
  #              reset    in
  test_cases = [ [ 0,     0 ], 
                 [ 1,    12 ], 
                 [ 0,    17 ], 
                 [ 0,    42 ], 
                 [ 1,   1024 ], 
                 [ 1,   9001 ], 
                 [ 1,  0x7fffffff ]
               ]
  random_tests = [ [ random.randint( 0, 1 ), random.randint( 0, 0x7fffffff ) ] 
    for x in range( 20 ) ]
  test_cases.extend( random_tests )

  for i,test in enumerate( test_cases[1:] ):
    model.reset.value = test[0]
    model.in_.value = test[1]
    sim.cycle()

    result = 0
    if test[0]:
      result = 0
    else:
      result = test[1]

    assert model.out.value == result

  #hdl = VerilogTranslationTool( model )
  #hdl.translate( "RegRst.v" )

#-------------------------------------------------------------------------
# Register with Enable unit tests
#-------------------------------------------------------------------------

def test_RegEn():

  model = RegEnRst( 32 )
  model.elaborate()

  sim = SimulationTool( model )
  #sim.dump_vcd( "RegEn_test.vcd" )

  sim.reset()
  #               en  in
  test_cases = [ [ 1,  0 ], 
                 [ 1, 12 ], 
                 [ 1, 17 ], 
                 [ 0, 42 ], 
                 [ 1, 1024 ], 
                 [ 1, 9001 ], 
                 [ 0, 0x7fffffff ]
               ]
  random_tests = [ [ random.randint( 0, 1 ), random.randint( 0, 0x7fffffff ) ] 
    for x in range( 20 ) ]
  test_cases.extend( random_tests )

  for i,test in enumerate( test_cases[1:] ):
    model.en.value = test[0]
    model.in_.value = test[1]
    prev_value = model.out.value
    sim.cycle()

    result = 0
    if test[0]:
      result = test[1]
    else:
      result = prev_value

    assert model.out.value == result

  #hdl = VerilogTranslationTool( model )
  #hdl.translate( "RegEn.v" )

#-------------------------------------------------------------------------
# Register with Enable and Reset unit test
#-------------------------------------------------------------------------

def test_RegEnRst():

  model = RegEnRst( 32 )
  model.elaborate()

  sim = SimulationTool( model )
  #sim.dump_vcd( "RegEnRst_test.vcd" )

  sim.reset()
  #              reset  en  in
  test_cases = [ [ 0,    1,  0 ], 
                 [ 1,    1, 12 ], 
                 [ 0,    1, 17 ], 
                 [ 0,    0, 42 ], 
                 [ 1,    1, 1024 ], 
                 [ 1,    1, 9001 ], 
                 [ 1,    0, 0x7fffffff ]
               ]
  random_tests = [ [ random.randint( 0, 1 ), random.randint( 0, 1 ), 
    random.randint( 0, 0x7fffffff ) ] for x in range( 20 ) ]
  test_cases.extend( random_tests )

  for i,test in enumerate( test_cases[1:] ):
    model.reset.value = test[0]
    model.en.value = test[1]
    model.in_.value = test[2]
    prev_value = model.out.value
    sim.cycle()

    result = 0
    if test[0]:
      result = 0
    elif test[1]:
      result = test[2]
    else:
      result = prev_value

    assert model.out.value == result

  #hdl = VerilogTranslationTool( model )
  #hdl.translate( "RegEnRst.v" )

