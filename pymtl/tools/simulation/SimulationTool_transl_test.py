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
# translation_slices14
#-----------------------------------------------------------------------
@pytest.mark.xfail(
  reason='Slicing of Bits with steps are not supported.',
  #raises=IndexError # TODO
)
def test_translation_slices14( setup_sim ):

  class TestTranslationSlices14( Model ):
    def __init__( s ):
      s.in_  = InPort ( 4 )
      s.even = OutPort( 2 )
      s.odd  = OutPort( 1 )

      @s.posedge_clk
      def logic0():
        s.even.next = s.in_[ ::2]
        s.odd .next = s.in_[1::2]

  m, sim = setup_sim( TestTranslationSlices14() )
  for i in range(10):
    k = Bits(4,randrange(0,2**4))
    m.in_.value = k
    sim.cycle()
    assert m.even == concat( m.in_[2], m.in_[0] )
    assert m.odd  == concat( m.in_[3], m.in_[1] )

#-----------------------------------------------------------------------
# translation_slices15
#-----------------------------------------------------------------------
@pytest.mark.parametrize( 'num', range(3) )
def test_translation_slices15( setup_sim, num ):

  class TestTranslationSlices15( Model ):
    def __init__( s, num ):
      s.in_ = InPort ( 4 )
      s.out = OutPort( 4 )

      if num == 0:
        @s.combinational
        def logic0():
          a = s.in_[0]
          b = s.in_[1]
          c = s.in_[2]
          d = s.in_[3]
          s.out.value = concat( d, c, b, a )

      elif num == 1:
        @s.combinational
        def logic0():
          a = s.in_[0:2]
          b = s.in_[2:4]
          s.out.value = concat( b, a )

      elif num == 2:
        @s.combinational
        def logic0():
          a = s.in_[0:4]
          s.out.value = a

      else: raise Exception('Invalid Configuration!')

  m, sim = setup_sim( TestTranslationSlices15( num ) )
  for i in range(10):
    k = Bits(4,randrange(0,2**4))
    m.in_.value = k
    sim.cycle()
    assert m.out == k

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
# translation_multiple_lhs_tuple
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
# translation_multiple_lhs_targets
#-----------------------------------------------------------------------
@pytest.mark.xfail(
  reason='Chained assignments are not supported (x = y = ...).'
)
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

#-----------------------------------------------------------------------
# translation_multiple_decorators
#-----------------------------------------------------------------------
def test_translation_multiple_decorators( setup_sim ):

  def test_decorator( fn ):
    return fn

  class TestTranslationMultipleDecorators( Model ):
    def __init__( s ):
      s.i0 = InPort ( 2 )
      s.o0 = OutPort( 2 )
      @test_decorator
      @s.combinational
      def logic0():
        s.o0.value = s.i0

  m, sim = setup_sim( TestTranslationMultipleDecorators() )
  for i in range(10):
    a = randrange(0,2**2)
    m.i0.value = a
    sim.cycle()
    assert m.o0 == a

#-----------------------------------------------------------------------
# translation_for_loop_enumerate
#-----------------------------------------------------------------------
def test_translation_for_loop_enumerate( setup_sim ):

  class TestTranslationLoopEnumerate( Model ):
    def __init__( s ):
      s.i = InPort [4]( 2 )
      s.o = OutPort[4]( 2 )
      @s.posedge_clk
      def logic0():
        for x, inport in enumerate( s.i ):
          s.o[x].next = inport

  m, sim = setup_sim( TestTranslationLoopEnumerate() )
  for i in range(10):
    js = [randrange(0,2**2) for _ in range( 4 )]
    for k in range(4): m.i[k].value = js[k]
    sim.cycle()
    for k in range(4): assert m.o[k] == js[k]

#-----------------------------------------------------------------------
# translation_for_loop_enumerate_comb
#-----------------------------------------------------------------------
@pytest.mark.xfail(
  reason='FIXME: Signals read in for loops are not added to sensitivity list!'
)
def test_translation_for_loop_enumerate_comb( setup_sim ):

  class TestTranslationLoopEnumerateComb( Model ):
    def __init__( s ):
      s.i = InPort [4]( 2 )
      s.o = OutPort[4]( 2 )
      @s.combinational
      def logic0():
        for x, inport in enumerate( s.i ):
          s.o[x].value = inport

  m, sim = setup_sim( TestTranslationLoopEnumerateComb() )
  for i in range(10):
    js = [randrange(0,2**2) for _ in range( 4 )]
    for k in range(4): m.i[k].value = js[k]
    sim.cycle()
    for k in range(4): assert m.o[k] == js[k]

#-----------------------------------------------------------------------
# test_translation_bad_decorator
#-----------------------------------------------------------------------
def test_translation_bad_decorator( setup_sim ):
  class TestTranslationBadDecorator( Model ):
    def __init__( s ):
      s.i = InPort ( 2 )
      s.o = OutPort( 2 )
      @s.tick_cl
      def logic0():
        s.o.next = s.i

  m, sim = setup_sim( TestTranslationBadDecorator() )
  for i in range(10):
    k = randrange(0,2**2)
    m.i.value = k
    sim.cycle()
    assert m.o == k

#-----------------------------------------------------------------------
# test_translation_bit_iterator
#-----------------------------------------------------------------------
def test_translation_bit_iterator( setup_sim ):
  class TestTranslationBitIterator( Model ):
    def __init__( s ):
      s.i = InPort ( 2 )
      s.o = OutPort( 2 )
      @s.tick_rtl
      def logic0():
        for x in range( 2 ):
          s.o[x].next = s.i[x]

  m, sim = setup_sim( TestTranslationBitIterator() )
  for i in range(10):
    k = randrange(0,2**2)
    m.i.value = k
    sim.cycle()
    assert m.o == k

#-----------------------------------------------------------------------
# test_translation_loopvar_port_name_conflict
#-----------------------------------------------------------------------
def test_translation_loopvar_port_name_conflict( setup_sim ):
  class TestTranslationLoopvarPortNameConflict( Model ):
    def __init__( s ):
      s.i = InPort ( 2 )
      s.o = OutPort( 2 )
      @s.tick_rtl
      def logic0():
        for i in range( 2 ):
          s.o[i].next = s.i[i]

  m, sim = setup_sim( TestTranslationLoopvarPortNameConflict() )
  for i in range(10):
    k = randrange(0,2**2)
    m.i.value = k
    sim.cycle()
    assert m.o == k

#-----------------------------------------------------------------------
# test_translation_bad_comparison
#-----------------------------------------------------------------------
@pytest.mark.parametrize('impl', range(4) )
def test_translation_bad_comparison( setup_sim, impl ):

  class TestTranslationBadComparison( Model ):
    def __init__( s, num ):
      s.i = InPort ( 2 )
      s.o = OutPort( 1 )

      if num == 0:
        @s.tick_rtl
        def logic0():
          s.o.next = 0 < s.i < 3

      if num == 1:
        @s.combinational
        def logic0():
          s.o.value = 0 < s.i < 3

      if num == 2:
        @s.tick_rtl
        def logic0():
          if 0 < s.i < 3: s.o.next = 1
          else:           s.o.next = 0

      if num == 3:
        @s.combinational
        def logic0():
          if 0 < s.i < 3: s.o.value = 1
          else:           s.o.value = 0

  m, sim = setup_sim( TestTranslationBadComparison(impl) )
  for i in range(10):
    k = randrange(0,2**2)
    m.i.value = k
    sim.cycle()
    assert m.o == (0 < k < 3)

#-----------------------------------------------------------------------
# translation_list_slice_temp
#-----------------------------------------------------------------------
@pytest.mark.parametrize( 'num', range(2) )
def test_translation_list_slice_temp( setup_sim, num ):

  class TestTranslationListSliceTemp( Model ):
    def __init__( s, num ):
      s.in_ = InPort [4]( 2 )
      s.o1  = OutPort[2]( 2 )
      s.o2  = OutPort[2]( 2 )

      if num == 0:
        s.evens = []
        s.odds  = []
        @s.posedge_clk
        def logic0():
          s.evens = s.in_[ ::2]
          s.odds  = s.in_[1::2]
          for i in range(2):
            s.o1[i].next = s.evens[i]
          for j in range(2):
            s.o2[j].next = s.odds[j]

      elif num == 1:
        @s.posedge_clk
        def logic0():
          evens = s.in_[ ::2]
          odds  = s.in_[1::2]
          for i in range(2):
            s.o1[i].next = evens[i]
          for j in range(2):
            s.o2[j].next = odds[j]

  m, sim = setup_sim( TestTranslationListSliceTemp(num) )
  for i in range(10):
    js = [randrange(0,2**2) for _ in range( 4 )]
    for k in range(4): m.in_[k].value = js[k]
    sim.cycle()
    for k, j in enumerate(js[ ::2]):
      assert m.o1[k] == j
    for k, j in enumerate(js[1::2]):
      assert m.o2[k] == j

#-----------------------------------------------------------------------
# translation_list_slice_step
#-----------------------------------------------------------------------
@pytest.mark.parametrize( 'num', range(2) )
def test_translation_list_slice_step( setup_sim, num ):

  class TestTranslationListSliceStep( Model ):
    def __init__( s, num ):
      s.in_ = InPort ( 4 )
      s.out = OutPort( 4 )

      @s.posedge_clk
      def logic0():
        for i in range(4)[ ::2]: s.out[i].next = not s.in_[i]
        for j in range(4)[1::2]: s.out[j].next =     s.in_[j]

  m, sim = setup_sim( TestTranslationListSliceStep(num) )
  for i in range(10):
    k = Bits(4,randrange(0,2**4))
    m.in_.value = k
    sim.cycle()
    for i in range( 4 ):
      if (i % 2): assert m.out[i] ==      k[i]
      else:       assert m.out[i] == (not k[i])

#-----------------------------------------------------------------------
# translation_unsupported_func
#-----------------------------------------------------------------------
def test_translation_unsupported_func( setup_sim ):

  class TestTranslationUnsupportedFunc( Model ):
    def __init__( s ):
      s.in_ = InPort [4]( 1 )
      s.out = OutPort   ( 4 )

      c = concat

      @s.combinational
      def logic0():
        s.out.value = c( s.in_[3], s.in_[2], s.in_[1], s.in_[0] )

  m, sim = setup_sim( TestTranslationUnsupportedFunc() )
  for i in range(10):
    k = Bits(4,randrange(0,2**4))
    for i in range(4):
      m.in_[i].value = k[i]
    sim.cycle()
    assert m.out == k

#-----------------------------------------------------------------------
# translation_func_not_int
#-----------------------------------------------------------------------
@pytest.mark.parametrize('num', range(6) )
def test_translation_func_not_int( setup_sim, num ):

  class TestTranslationFuncNotInt( Model ):
    def __init__( s, num ):
      s.in_ = InPort ( 4 )
      s.out = OutPort( 8 )

      if num == 0:
        @s.combinational
        def logic0():
          s.out.value = sext( s.in_, 8.1 )

      elif num == 1:
        @s.combinational
        def logic0():
          s.out.value = zext( s.in_, 8.1 )

      elif num == 2:
        @s.combinational
        def logic0():
          s.out.value = Bits( 8.1, s.in_ )

      elif num == 3:
        @s.combinational
        def logic0():
          s.out.value = sext( s.in_, 4+4 )

      elif num == 4:
        @s.combinational
        def logic0():
          s.out.value = zext( s.in_, 4+4 )

      elif num == 5:
        @s.combinational
        def logic0():
          s.out.value = Bits( 4+4, s.in_ )

      else:
        raise Exception('Invalid Configuration!')

  m, sim = setup_sim( TestTranslationFuncNotInt(num) )
  for i in range(10):
    k = Bits(4,randrange(0,2**4))
    m.in_.value = k
    sim.cycle()
    if   num == 0: assert m.out == sext( k, 8 )
    elif num == 1: assert m.out == k
    elif num == 2: assert m.out == k

#-----------------------------------------------------------------------
# translation_func_not_int_inf
#-----------------------------------------------------------------------
@pytest.mark.parametrize('num', range(3) )
def test_translation_inf_func_not_int( setup_sim, num ):

  class TestTranslationInfFuncNotInt( Model ):
    def __init__( s, num ):
      s.in_ = InPort ( 4 )
      s.out = OutPort( 8 )

      new_bw = Bits(4,8)

      if num == 0:
        @s.combinational
        def logic0():
          tmp = sext( s.in_, new_bw )
          s.out.value = tmp

      elif num == 1:
        @s.combinational
        def logic0():
          tmp = zext( s.in_, new_bw )
          s.out.value = tmp

      elif num == 2:
        @s.combinational
        def logic0():
          tmp = Bits( new_bw, s.in_ )
          s.out.value = tmp

      else:
        raise Exception('Invalid Configuration!')

  m, sim = setup_sim( TestTranslationInfFuncNotInt(num) )
  for i in range(10):
    k = Bits(4,randrange(0,2**4))
    m.in_.value = k
    sim.cycle()
    if   num == 0: assert m.out == sext( k, 8 )
    elif num == 1: assert m.out == k
    elif num == 2: assert m.out == k

#-----------------------------------------------------------------------
# translation_reverse_iter
#-----------------------------------------------------------------------
@pytest.mark.parametrize('num', range(8) )
def test_translation_reverse_iter( setup_sim, num ):

  class TestTranslationReverseIter( Model ):
    def __init__( s, num ):
      s.in_ = InPort ( 8 )
      s.out = OutPort( 8 )

      if num == 0:
        @s.combinational
        def logic0():
          for i in range( 8 ):
            s.out[i].value = s.in_[i]

      elif num == 1:
        @s.combinational
        def logic0():
          for i in range( 0, 8, 2 ):
            s.out[i].value = s.in_[i]
          for i in range( 1, 8, 2 ):
            s.out[i].value = s.in_[i]

      elif num == 2:
        @s.combinational
        def logic0():
          for i in xrange( 8 ):
            s.out[i].value = s.in_[i]

      elif num == 3:
        @s.combinational
        def logic0():
          for i in xrange( 0, 8, 2 ):
            s.out[i].value = s.in_[i]
          for i in xrange( 1, 8, 2 ):
            s.out[i].value = s.in_[i]

      elif num == 4:
        @s.combinational
        def logic0():
          for i in range( 7,-1,-1 ):
            s.out[i].value = s.in_[i]

      elif num == 5:
        @s.combinational
        def logic0():
          for i in range( 7, -1, -2 ):
            s.out[i].value = s.in_[i]
          for i in range( 6, -1, -2 ):
            s.out[i].value = s.in_[i]

      elif num == 6:
        step = 1
        @s.combinational
        def logic0():
          for i in range( 0,8,step ):
            s.out[i].value = s.in_[i]

      elif num == 7:
        step = -1
        @s.combinational
        def logic0():
          for i in range( 7,-1,step ):
            s.out[i].value = s.in_[i]

      else:
        raise Exception('Invalid Configuration!')

  n = 4
  m, sim = setup_sim( TestTranslationReverseIter(num) )
  for i in range(10):
    k = Bits(n,randrange(0,2**n))
    m.in_.value = k
    sim.cycle()
    assert m.out == k

#-----------------------------------------------------------------------
# translation_iter_unsupported_step
#-----------------------------------------------------------------------
@pytest.mark.parametrize('num',
  [pytest.mark.xfail(reason='Range w/ step= 0')(0), 1, 2,]
)
def test_translation_iter_unsupported_step( setup_sim, num ):

  class TestTranslationIterUnsupportedStep( Model ):
    def __init__( s, num ):
      s.in_ = InPort ( 8 )
      s.out = OutPort( 8 )

      if num == 0:
        @s.combinational
        def logic0():
          for i in range( 0, 8, 0 ):
            s.out[i].value = s.in_[i]
      elif num == 1:
        @s.combinational
        def logic0():
          for i in range( 0, 8, 0+1 ):
            s.out[i].value = s.in_[i]
      elif num == 2:
        @s.combinational
        def logic0():
          for i in range( 7,-1, 0-1 ):
            s.out[i].value = s.in_[i]

      else:
        raise Exception('Invalid Configuration!')

  n = 4
  m, sim = setup_sim( TestTranslationIterUnsupportedStep(num) )
  for i in range(10):
    k = Bits(n,randrange(0,2**n))
    m.in_.value = k
    sim.cycle()
    assert m.out == k

#-----------------------------------------------------------------------
# translation_keyword_args
#-----------------------------------------------------------------------
@pytest.mark.parametrize('num', range(3))
def test_translation_keyword_args( setup_sim, num ):

  class TestTranslationKeywordArgs( Model ):
    def __init__( s, num ):
      s.a   = InPort ( 8 )
      s.b   = InPort ( 8 )
      s.out = OutPort( 8 )

      if num == 0:
        @s.posedge_clk
        def logic():
          s.out.next = Bits(8, 4, trunc=True)
          print s.out.value

      elif num == 1:
        my_args = [8,4]
        @s.posedge_clk
        def logic():
          s.out.next = Bits( *my_args )

      elif num == 2:
        my_args = { 'nbits':8, 'value':4 }
        @s.posedge_clk
        def logic():
          s.out.next = Bits( **my_args )

      else:
        raise Exception('Invalid Configuration!')

  m, sim = setup_sim( TestTranslationKeywordArgs(num) )
  for i in range(10):
    sim.cycle()
    assert m.out == 4

#-----------------------------------------------------------------------
# translation_issue_123
#-----------------------------------------------------------------------
@pytest.mark.parametrize('num', range(4))
def test_translation_issue_123( setup_sim, num ):

  class TestTranslationIssue123( Model ):
    def __init__( s, num ):
      s.a   = InPort ( 8 )
      s.b   = InPort ( 8 )
      s.out = OutPort( 16 )

      if num == 0:
        @s.combinational
        def logic():
          s.out.value = Bits(16, s.a*s.b, True)

      elif num == 1:
        @s.combinational
        def logic():
          s.out.value = Bits(16, s.a*s.b)

      elif num == 2:
        @s.combinational
        def logic():
          s.out.value = Bits(16, s.a)

      elif num == 3:
        @s.combinational
        def logic():
          s.out.value = Bits(8+8, s.a)

      else:
        raise Exception('Invalid Configuration!')

  m, sim = setup_sim( TestTranslationIssue123(num) )
  for i in range(10):
    a, b = [randrange(2**8) for _ in range(2)]
    m.a.value, m.b.value = a, b
    sim.cycle()
    if num == 0: assert m.out == m.a*m.b
    if num == 1: assert m.out == m.a*m.b
    if num == 2: assert m.out == m.a
    if num == 3: assert m.out == m.a

#-----------------------------------------------------------------------
# translation_bits_constr
#-----------------------------------------------------------------------
@pytest.mark.parametrize('num', range(6))
def test_translation_bits_constr( setup_sim, num ):

  class TestTranslationBitsConstr( Model ):
    def __init__( s, num ):
      s.a   = InPort ( 8 )
      s.out = OutPort( 16 )

      if num == 0:
        @s.posedge_clk
        def logic():
          s.out.next = Bits(16)

      elif num == 1:
        @s.posedge_clk
        def logic():
          s.out.next = Bits(16, 1)

      elif num == 2:
        s.tmp = num
        @s.posedge_clk
        def logic():
          s.out.next = Bits(16, s.tmp)

      elif num == 3:
        tmp = num
        @s.posedge_clk
        def logic():
          s.out.next = Bits(16, tmp)

      elif num == 4:
        s.tmp = 16
        @s.posedge_clk
        def logic():
          s.out.next = Bits(s.tmp, 4)

      elif num == 5:
        tmp = 16
        @s.posedge_clk
        def logic():
          s.out.next = Bits(tmp, 5)

      else:
        raise Exception('Invalid Configuration!')

  m, sim = setup_sim( TestTranslationBitsConstr(num) )
  for i in range(10):
    sim.cycle()
    assert m.out == num

#-----------------------------------------------------------------------
# translation_issue_88
#-----------------------------------------------------------------------
@pytest.mark.parametrize('num', range(2))
def test_translation_issue_88( setup_sim, num ):

  class TestTranslationIssue88( Model ):
    def __init__( s, num, nports=2, size=4 ):
      clog2   = get_sel_nbits
      addr_sz = clog2( size )

      s.wr_addr = InPort [nports]( addr_sz )
      s.wr_data = InPort [nports]( 8 )
      s.rd_data = OutPort[size  ]( 8 )

      s.regs     = Wire[size]( 8 )

      if   num == 0:
        @s.posedge_clk
        def write_logic():
          for i in range( nports ):
            s.regs[ s.wr_addr[i] ].next = s.wr_data[i]

      elif num == 1:
        @s.posedge_clk
        def write_logic():
          for i in range( nports ):
            j = s.wr_addr[i]
            s.regs[ j ].next = s.wr_data[i]

      else:
        raise Exception('Invalid Configuration!')

      @s.combinational
      def read_logic():
        for i in range( size ):
          s.rd_data[i].value = s.regs[i]

  m, sim = setup_sim( TestTranslationIssue88( num ) )
  for i in range(10):
    # ensure no addr conflict in write ports
    a_addr, b_addr = randrange(0,2), randrange(2,4)
    a_data, b_data = [randrange(0,2**8) for _ in range(2)]
    m.wr_addr[0].value = a_addr
    m.wr_addr[1].value = b_addr
    m.wr_data[0].value = a_data
    m.wr_data[1].value = b_data
    sim.cycle()
    assert m.rd_data[ a_addr ] == a_data
    assert m.rd_data[ b_addr ] == b_data

#-----------------------------------------------------------------------
# translation_issue_136
#-----------------------------------------------------------------------
def test_translation_issue_136( setup_sim ):
  class TestTranslationIssue136( Model ):
    def __init__( s ):
      s.a = InPort [ 2 ]( 4 )
      s.b = OutPort[ 2 ]( 4 )

      @s.combinational
      def logic():
        j = s.a[0]
        s.b[0].value = j
        s.b[1].value = s.a[1]

  m, sim = setup_sim( TestTranslationIssue136() )
  for i in range(10):
    a = [randrange(2**4) for _ in range(2)]
    m.a[0].value, m.a[1].value = a
    sim.cycle()
    assert m.b[0] == a[0]
    assert m.b[1] == a[1]



#'TODO: negative indexes: my_signal[-2]   issue #31
#'TODO: negative indexes: my_signal[0:-2] issue #31

# TODO: invalid number of arguments to range/xrange
# TODO: support reversed( range(...) )

# TODO: member variable with empty list
# TODO: member variable with ints in list
# TODO: member variable with Bits in list

