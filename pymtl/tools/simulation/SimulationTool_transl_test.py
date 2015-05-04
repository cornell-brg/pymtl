#=======================================================================
# SimulationTool_transl_test.py
#=======================================================================
'''Collection of tests to document RTL translation issues.'''

import pytest

from pymtl  import *
from random import randrange

from SimulationTool_seq_test import setup_sim, local_setup_sim

bits  = get_nbits
clog2 = get_sel_nbits

#-----------------------------------------------------------------------
# translation_slices00
#-----------------------------------------------------------------------
def test_translation_slices00( setup_sim ):

  class TestTranslationSlices00( Model ):
    def __init__( s ):
      s.i = InPort    ( 16 )
      s.o = OutPort[8](  2 )
      s.j = Wire      ( bits(16) )
      @s.combinational
      def logic():
        for x in range( 8 ):
          s.j.value = 2*x
          s.o[x].value = s.i[s.j:s.j+2]

  m, sim = setup_sim( TestTranslationSlices00() )
  for i in range(10):
    val = randrange(0,2**16)
    m.i.value = val
    sim.cycle()
    assert concat( *[x for x in reversed(m.o)] ) == val

#-----------------------------------------------------------------------
# translation_slices01
#-----------------------------------------------------------------------
def test_translation_slices01( setup_sim ):

  class TestTranslationSlices01( Model ):
    def __init__( s ):
      s.i = InPort     ( 16 )
      s.o = OutPort[16](  1 )
      s.j = Wire       ( bits(16) )
      @s.combinational
      def logic():
        for x in range( 16 ):
          s.o[x].value = s.i[x:x+1]

  m, sim = setup_sim( TestTranslationSlices01() )
  for i in range(10):
    val = randrange(0,2**16)
    m.i.value = val
    sim.cycle()
    assert concat( *[x for x in reversed(m.o)] ) == val

#-----------------------------------------------------------------------
# translation_slices02
#-----------------------------------------------------------------------
def test_translation_slices02( setup_sim ):
  class TestTranslationSlices02( Model ):
    def __init__( s ):
      s.i = InPort ( 16 )
      s.o = OutPort(  8 )
      off = 8
      @s.combinational
      def logic():
        s.o.value = s.i[0:off]
  m, sim = setup_sim( TestTranslationSlices02() )
  for i in range(10):
    val = Bits(16, randrange(0,2**16) )
    m.i.value = val
    sim.cycle()
    assert m.o == val[:8]

#-----------------------------------------------------------------------
# translation_slices03
#-----------------------------------------------------------------------
def test_translation_slices03( setup_sim ):
  class TestTranslationSlices03( Model ):
    def __init__( s ):
      s.i = InPort ( 16 )
      s.o = OutPort(  6 )
      off = 8
      @s.combinational
      def logic():
        s.o.value = s.i[0:off-2]
  m, sim = setup_sim( TestTranslationSlices03() )
  for i in range(10):
    val = Bits(16, randrange(0,2**16) )
    m.i.value = val
    sim.cycle()
    assert m.o == val[:8-2]

#-----------------------------------------------------------------------
# translation_slices04
#-----------------------------------------------------------------------
def test_translation_slices04( setup_sim ):
  class TestTranslationSlices04( Model ):
    def __init__( s ):
      s.i = InPort ( 16 )
      s.o = OutPort( 10 )
      off = 8
      @s.combinational
      def logic():
        s.o.value = s.i[0:off+2]
  m, sim = setup_sim( TestTranslationSlices04() )
  for i in range(10):
    val = Bits(16, randrange(0,2**16) )
    m.i.value = val
    sim.cycle()
    assert m.o == val[:8+2]

#-----------------------------------------------------------------------
# translation_slices05
#-----------------------------------------------------------------------
def test_translation_slices05( setup_sim ):
  class TestTranslationSlices05( Model ):
    def __init__( s ):
      s.i = InPort ( 16 )
      s.o = OutPort(  8 )
      off = 8
      @s.combinational
      def logic():
        s.o.value = s.i[:off]
  m, sim = setup_sim( TestTranslationSlices05() )
  for i in range(10):
    val = Bits(16, randrange(0,2**16) )
    m.i.value = val
    sim.cycle()
    assert m.o == val[:8]

#-----------------------------------------------------------------------
# translation_slices06
#-----------------------------------------------------------------------
def test_translation_slices06( setup_sim ):
  class TestTranslationSlices06( Model ):
    def __init__( s ):
      s.i = InPort ( 16 )
      s.o = OutPort(  8 )
      off = 8; stop = 16
      @s.combinational
      def logic():
        s.o.value = s.i[off:stop]
  m, sim = setup_sim( TestTranslationSlices06() )
  for i in range(10):
    val = Bits(16, randrange(0,2**16) )
    m.i.value = val
    sim.cycle()
    assert m.o == val[8:]

#-----------------------------------------------------------------------
# translation_slices07
#-----------------------------------------------------------------------
def test_translation_slices07( setup_sim ):
  class TestTranslationSlices07( Model ):
    def __init__( s ):
      s.i = InPort ( 16 )
      s.o = OutPort(  8 )
      off = 8
      @s.combinational
      def logic():
        s.o.value = s.i[off:]
  m, sim = setup_sim( TestTranslationSlices07() )
  for i in range(10):
    val = Bits(16, randrange(0,2**16) )
    m.i.value = val
    sim.cycle()
    assert m.o == val[8:]

#-----------------------------------------------------------------------
# translation_slices08
#-----------------------------------------------------------------------
@pytest.mark.xfail(
  reason='Bad bitwidth extension results in [12:0] instead of [12:16]'
)
def test_translation_slices08( setup_sim ):

  class TestTranslationSlices08( Model ):
    def __init__( s ):
      s.i = InPort ( 16 )
      s.o = OutPort(  4 )
      s.j = InPort ( clog2(4) )
      @s.combinational
      def logic():
        s.o.value = s.i[s.j*4:s.j*4+4]

  m, sim = setup_sim( TestTranslationSlices08() )
  val       = Bits(16, randrange(0,2**16))
  m.i.value = val
  for i in range(4):
    m.j.value = i
    sim.cycle()
    assert m.o == val[i*4:i*4+4]

#-----------------------------------------------------------------------
# translation_slices09
#-----------------------------------------------------------------------
def test_translation_slices09( setup_sim ):

  class TestTranslationSlices09( Model ):
    def __init__( s ):
      s.i = InPort ( 16 )
      s.o = OutPort(  4 )
      s.j = InPort ( clog2(4)+1 )
      @s.combinational
      def logic():
        s.o.value = s.i[s.j*4:s.j*4+4]

  m, sim = setup_sim( TestTranslationSlices09() )
  val       = Bits(16, randrange(0,2**16))
  m.i.value = val
  for i in range(4):
    m.j.value = i
    sim.cycle()
    assert m.o == val[i*4:i*4+4]

#-----------------------------------------------------------------------
# translation_slices10
#-----------------------------------------------------------------------
def test_translation_slices10( setup_sim ):

  class TestTranslationSlices10( Model ):
    def __init__( s ):
      s.i = InPort ( 16 )
      s.o = OutPort(  4 )
      s.j = InPort ( clog2(4)+1 )
      @s.combinational
      def logic():
        s.o.value = s.i[4*s.j:4*s.j+4]

  m, sim = setup_sim( TestTranslationSlices10() )
  val       = Bits(16, randrange(0,2**16))
  m.i.value = val
  for i in range(4):
    m.j.value = i
    sim.cycle()
    assert m.o == val[i*4:i*4+4]

#-----------------------------------------------------------------------
# translation_slices11
#-----------------------------------------------------------------------
def test_translation_slices11( setup_sim ):

  class TestTranslationSlices11( Model ):
    def __init__( s ):
      s.i = InPort ( 16 )
      s.o = OutPort(  4 )
      s.j = InPort ( clog2(4)+1 )
      @s.combinational
      def logic():
        s.o.value = s.i[4*s.j:s.j*4+4]

  m, sim = setup_sim( TestTranslationSlices11() )
  val       = Bits(16, randrange(0,2**16))
  m.i.value = val
  for i in range(4):
    m.j.value = i
    sim.cycle()
    assert m.o == val[i*4:i*4+4]

#-----------------------------------------------------------------------
# translation_slices12
#-----------------------------------------------------------------------
@pytest.mark.xfail(
  reason='This should not work because bitslice changes bitwidth!'
)
def test_translation_slices12( setup_sim ):

  class TestTranslationSlices12( Model ):
    def __init__( s ):
      s.i = InPort ( 16 )
      s.o = OutPort(  4 )
      s.j = InPort ( clog2(4)+1 )
      @s.combinational
      def logic():
        s.o.value = s.i[0:(s.j+1)*4]

  m, sim = setup_sim( TestTranslationSlices12() )
  val       = Bits(16, randrange(0,0))
  m.i.value = val
  for i in range(4):
    m.j.value = i
    sim.cycle()
    assert m.o == val[0:(i+1)*4]

#-----------------------------------------------------------------------
# translation_slices13
#-----------------------------------------------------------------------
def test_translation_slices13( setup_sim ):

  class TestTranslationSlices13( Model ):
    def __init__( s ):
      s.i = InPort ( 16 )
      s.o = OutPort(  4 )
      s.j = InPort ( clog2(4)+1 )
      @s.combinational
      def logic():
        s.o.value = s.i[s.j*4:s.j*4+2+2]

  m, sim = setup_sim( TestTranslationSlices13() )
  val       = Bits(16, randrange(0,2**16))
  m.i.value = val
  for i in range(4):
    m.j.value = i
    sim.cycle()
    assert m.o == val[i*4:i*4+4]

#-----------------------------------------------------------------------
# translation_slices07
#-----------------------------------------------------------------------
#def test_translation_slices07( setup_sim ):
#  class TestTranslationSlices07( Model ):
#    def __init__( s ):
#      s.i = InPort ( 16 )
#      s.o = OutPort(  8 )
#      off = 8
#      @s.combinational
#      def logic():
#        s.o.value = s.i[off:]
#  m, sim = setup_sim( TestTranslationSlices07() )
#  for i in range(10):
#    val = Bits(16, randrange(0,2**16) )
#    m.i.value = val
#    sim.cycle()
#    assert m.o == val[8:]

#-----------------------------------------------------------------------
# translation_true_false
#-----------------------------------------------------------------------
def test_translation_true_false( setup_sim ):

  class TestTranslationTrueFalse( Model ):
    def __init__( s ):
      s.i = InPort ( 2 )
      s.o = OutPort( 1 )
      @s.combinational
      def logic():
        if s.i > 2: s.o.value = True
        else:       s.o.value = False

  m, sim = setup_sim( TestTranslationTrueFalse() )
  for i in range(10):
    val = randrange(0,2**2)
    m.i.value = val
    sim.cycle()
    assert m.o == (val > 2)

#-----------------------------------------------------------------------
# translation_temporary_scope
#-----------------------------------------------------------------------
def test_translation_temporary_scope( setup_sim ):

  class TestTranslationTemporaryScope( Model ):
    def __init__( s ):
      s.a = InPort ( 2 )
      s.b = InPort ( 2 )
      s.o = OutPort( 1 )
      s.p = OutPort( 1 )
      @s.combinational
      def logic0():
        temp = s.a > s.b
        s.o.value = temp

      @s.combinational
      def logic1():
        temp = s.b < s.a
        s.p.value = temp

  m, sim = setup_sim( TestTranslationTemporaryScope() )
  for i in range(10):
    a,b = [randrange(0,2**2) for _ in range(2)]
    m.a.value, m.b.value = a, b
    sim.cycle()
    assert m.o == (1 if a > b else 0)
    assert m.p == (1 if a > b else 0)

#-----------------------------------------------------------------------
# translation_temporary_multiple_lhs_tuple
#-----------------------------------------------------------------------
def test_translation_multiple_lhs_tuple( setup_sim ):

  class TestTranslationMultipleLHS_Tuple( Model ):
    def __init__( s ):
      s.i0 = InPort ( 2 )
      s.i1 = InPort ( 2 )
      s.o0 = OutPort( 2 )
      s.o1 = OutPort( 2 )
      @s.combinational
      def logic0():
        s.o0.value, s.o1.value = s.i0, s.i1

  m, sim = setup_sim( TestTranslationMultipleLHS_Tuple() )
  for i in range(10):
    a,b = [randrange(0,2**2) for _ in range(2)]
    m.i0.value, m.i1.value = a, b
    sim.cycle()
    assert m.o0 == a
    assert m.o1 == b

#-----------------------------------------------------------------------
# translation_temporary_multiple_lhs_targets
#-----------------------------------------------------------------------
@pytest.mark.xfail
def test_translation_multiple_lhs_targets( setup_sim ):

  class TestTranslationMultipleLHS_Targets( Model ):
    def __init__( s ):
      s.i0 = InPort ( 2 )
      s.o0 = OutPort( 2 )
      s.o1 = OutPort( 2 )
      @s.combinational
      def logic0():
        s.o0.value = s.o1.value = s.i0

  m, sim = setup_sim( TestTranslationMultipleLHS_Targets() )
  for i in range(10):
    a = randrange(0,2**2)
    m.i0.value = a
    sim.cycle()
    assert m.o0 == a
    assert m.o1 == a

