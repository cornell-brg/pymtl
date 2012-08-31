#=========================================================================
# Unit Tests for Muxes
#=========================================================================

from muxes import *
import random as r

#-------------------------------------------------------------------------
# 2-Input Mux and unit tests
#-------------------------------------------------------------------------

def test_Mux2():
  model = Mux2( 32 )
  model.elaborate()
  sim = SimulationTool( model )
  #sim.dump_vcd( "Mux2_test.vcd" )

  #                in0     in1   sel
  test_cases = [ [ 0,       1,    1 ],
                 [ 3,       4,    0 ],
                 [ 18,     25,    1 ],
                 [ 42,     17,    0 ],
                 [ 9001,  1024,   0 ]
               ]
  random_tests = [ [ r.randint( 0, 0xffffffff ), r.randint( 0, 0xffffffff ), 
                     r.randint( 0, 1 ) ] for x in range( 20 ) ]
  test_cases.extend( random_tests )

  for test in test_cases:
    model.in0.value = test[0]
    model.in1.value = test[1]
    model.sel.value = test[2]
    sim.cycle()

    result = test[ test[2] ]
    assert model.out.value == result

  #hdl = VerilogTranslationTool( model )
  #hdl.translate( "Mux2.v" )
  
#-------------------------------------------------------------------------
# 3-Input Mux and unit tests
#-------------------------------------------------------------------------

def test_Mux3():
  model = Mux3( 32 )
  model.elaborate()
  sim = SimulationTool( model )
  #sim.dump_vcd( "Mux3_test.vcd" )

  #                in0     in1   in2   sel
  test_cases = [ [ 0,       1,   39,    2 ],
                 [ 3,       4,   44,    0 ],
                 [ 18,     25,   2,     1 ],
                 [ 42,     17,   99,    2 ],
                 [ 9001,  1024,  0,     0 ]
               ]
  random_tests = [ [ r.randint( 0, 0xffffffff ), r.randint( 0, 0xffffffff ), 
                     r.randint( 0, 0xffffffff ),  
                     r.randint( 0, 2 ) ] for x in range( 20 ) ]
  test_cases.extend( random_tests )

  for test in test_cases:
    model.in0.value = test[0]
    model.in1.value = test[1]
    model.in2.value = test[2]
    model.sel.value = test[3]
    sim.cycle()

    result = test[ test[3] ]
    assert model.out.value == result

  #hdl = VerilogTranslationTool( model )
  #hdl.translate( "Mux3.v" )
  
#-------------------------------------------------------------------------
# 4-Input Mux and unit tests
#-------------------------------------------------------------------------

def test_Mux4():
  model = Mux4( 32 )
  model.elaborate()
  sim = SimulationTool( model )
  #sim.dump_vcd( "Mux4_test.vcd" )

  #                in0     in1   in2   in3   sel
  test_cases = [ [ 0,       1,   39,   22,    0 ],
                 [ 3,       4,   44,   44,    1 ],
                 [ 18,     25,   2,    99,    2 ],
                 [ 42,     17,   99,   88,    3 ],
                 [ 9001,  1024,  0,    77,    3 ]
               ]
  random_tests = [ [ r.randint( 0, 0xffffffff ), r.randint( 0, 0xffffffff ), 
                     r.randint( 0, 0xffffffff ), r.randint( 0, 0xffffffff ), 
                     r.randint( 0, 3 ) ] for x in range( 20 ) ]
  test_cases.extend( random_tests )

  for test in test_cases:
    model.in0.value = test[0]
    model.in1.value = test[1]
    model.in2.value = test[2]
    model.in3.value = test[3]
    model.sel.value = test[4]
    sim.cycle()

    result = test[ test[4] ]
    assert model.out.value == result

  #hdl = VerilogTranslationTool( model )
  #hdl.translate( "Mux4.v" )
  
#-------------------------------------------------------------------------
# 5-Input Mux and unit tests
#-------------------------------------------------------------------------

def test_Mux5():
  model = Mux5( 32 )
  model.elaborate()
  sim = SimulationTool( model )
  #sim.dump_vcd( "Mux5_test.vcd" )

  #                in0     in1   in2   in3   in4   sel
  test_cases = [ [ 0,       1,   39,   22,   33,    0 ],
                 [ 3,       4,   44,   44,   55,    1 ],
                 [ 18,     25,   2,    99,   66,    2 ],
                 [ 42,     17,   99,   88,   11,    3 ],
                 [ 9001,  1024,  0,    77,   100,   4 ]
               ]
  random_tests = [ [ r.randint( 0, 0xffffffff ), r.randint( 0, 0xffffffff ), 
                     r.randint( 0, 0xffffffff ), r.randint( 0, 0xffffffff ), 
                     r.randint( 0, 0xffffffff ),  
                     r.randint( 0, 4 ) ] for x in range( 20 ) ]
  test_cases.extend( random_tests )

  for test in test_cases:
    model.in0.value = test[0]
    model.in1.value = test[1]
    model.in2.value = test[2]
    model.in3.value = test[3]
    model.in4.value = test[4]
    model.sel.value = test[5]
    sim.cycle()

    result = test[ test[5] ]
    assert model.out.value == result

  #hdl = VerilogTranslationTool( model )
  #hdl.translate( "Mux5.v" )
  
#-------------------------------------------------------------------------
# 6-Input Mux and unit tests
#-------------------------------------------------------------------------

def test_Mux6():
  model = Mux6( 32 )
  model.elaborate()
  sim = SimulationTool( model )
  #sim.dump_vcd( "Mux6_test.vcd" )

  #                in0     in1   in2   in3   in4   in5,  sel
  test_cases = [ [ 0,       1,   39,   22,   33,   10,    0 ],
                 [ 3,       4,   44,   44,   55,   20,    1 ],
                 [ 18,     25,   2,    99,   66,   30,    2 ],
                 [ 42,     17,   99,   88,   11,   40,    3 ],
                 [ 47,     19,   91,   80,   101,  50,    4 ],
                 [ 9001,  1024,  0,    77,   100,  60,    5 ]
               ]
  random_tests = [ [ r.randint( 0, 0xffffffff ), r.randint( 0, 0xffffffff ), 
                     r.randint( 0, 0xffffffff ), r.randint( 0, 0xffffffff ), 
                     r.randint( 0, 0xffffffff ), r.randint( 0, 0xffffffff ), 
                     r.randint( 0, 5 ) ] for x in range( 20 ) ]
  test_cases.extend( random_tests )

  for test in test_cases:
    model.in0.value = test[0]
    model.in1.value = test[1]
    model.in2.value = test[2]
    model.in3.value = test[3]
    model.in4.value = test[4]
    model.in5.value = test[5]
    model.sel.value = test[6]
    sim.cycle()

    result = test[ test[6] ]
    assert model.out.value == result

  #hdl = VerilogTranslationTool( model )
  #hdl.translate( "Mux6.v" )
  
#-------------------------------------------------------------------------
# 7-Input Mux and unit tests
#-------------------------------------------------------------------------

def test_Mux7():
  model = Mux7( 32 )
  model.elaborate()
  sim = SimulationTool( model )
  #sim.dump_vcd( "Mux7_test.vcd" )

  #                in0     in1   in2   in3   in4   in5,  in6  sel
  test_cases = [ [ 0,       1,   39,   22,   33,   10,   70,   0 ],
                 [ 3,       4,   44,   44,   55,   20,   90,   1 ],
                 [ 18,     25,   2,    99,   66,   30,   111,  2 ],
                 [ 42,     17,   99,   88,   11,   40,   222,  3 ],
                 [ 47,     19,   91,   80,   101,  50,   333,  4 ],
                 [ 49,     5,    6 ,   32,   64,   128,  444,  5 ],
                 [ 9001,  1024,  0,    77,   100,  60,   555,  6 ]
               ]
  random_tests = [ [ r.randint( 0, 0xffffffff ), r.randint( 0, 0xffffffff ), 
                     r.randint( 0, 0xffffffff ), r.randint( 0, 0xffffffff ), 
                     r.randint( 0, 0xffffffff ), r.randint( 0, 0xffffffff ), 
                     r.randint( 0, 0xffffffff ), 
                     r.randint( 0, 6 ) ] for x in range( 20 ) ]
  test_cases.extend( random_tests )

  for test in test_cases:
    model.in0.value = test[0]
    model.in1.value = test[1]
    model.in2.value = test[2]
    model.in3.value = test[3]
    model.in4.value = test[4]
    model.in5.value = test[5]
    model.in6.value = test[6]
    model.sel.value = test[7]
    sim.cycle()

    result = test[ test[7] ]
    assert model.out.value == result

  #hdl = VerilogTranslationTool( model )
  #hdl.translate( "Mux7.v" )
  
#-------------------------------------------------------------------------
# 8-Input Mux and unit tests
#-------------------------------------------------------------------------

def test_Mux8():
  model = Mux8( 32 )
  model.elaborate()
  sim = SimulationTool( model )
  #sim.dump_vcd( "Mux8_test.vcd" )

  #                in0     in1   in2   in3   in4   in5,  in6  in7  sel
  test_cases = [ [ 0,       1,   39,   22,   33,   10,   70,  666,  0 ],
                 [ 3,       4,   44,   44,   55,   20,   90,  777,  1 ],
                 [ 18,     25,   2,    99,   66,   30,   111, 888,  2 ],
                 [ 42,     17,   99,   88,   11,   40,   222, 999,  3 ],
                 [ 47,     19,   91,   80,   101,  50,   333, 1111, 4 ],
                 [ 49,     5,    6 ,   32,   64,   128,  444, 2222, 5 ],
                 [ 65,     15,   25,   35,   45,   75,    85, 3333, 6 ],
                 [ 9001,  1024,  0,    77,   100,  60,   555, 4444, 7 ]
               ]
  random_tests = [ [ r.randint( 0, 0xffffffff ), r.randint( 0, 0xffffffff ), 
                     r.randint( 0, 0xffffffff ), r.randint( 0, 0xffffffff ), 
                     r.randint( 0, 0xffffffff ), r.randint( 0, 0xffffffff ), 
                     r.randint( 0, 0xffffffff ), r.randint( 0, 0xffffffff ), 
                     r.randint( 0, 7 ) ] for x in range( 20 ) ]
  test_cases.extend( random_tests )

  for test in test_cases:
    model.in0.value = test[0]
    model.in1.value = test[1]
    model.in2.value = test[2]
    model.in3.value = test[3]
    model.in4.value = test[4]
    model.in5.value = test[5]
    model.in6.value = test[6]
    model.in7.value = test[7]
    model.sel.value = test[8]
    sim.cycle()

    result = test[ test[8] ]
    assert model.out.value == result

  #hdl = VerilogTranslationTool( model )
  #hdl.translate( "Mux8.v" )
  
