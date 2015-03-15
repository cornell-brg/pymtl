#=======================================================================
# SimulationTool_wire_test.py
#=======================================================================
# Tests using wires for the SimulationTool class.

import pytest

from pymtl import *

from SimulationTool_seq_test  import setup_sim, local_setup_sim

#-----------------------------------------------------------------------
# Pipeline Tester
#-----------------------------------------------------------------------

def pipeline_tester( setup_sim, model, nstages ):
  model, sim = setup_sim( model )

  # fill up the pipeline
  for i in range( 10 ):
    model.in_.v = i
    expected = ( i - nstages + 1 ) if ( i - nstages + 1 ) >= 0 else 0
    assert model.out == expected
    sim.cycle()
  # drain the pipeline
  for i in range( 10 - nstages + 1, 10 ):
    assert model.out == i
    sim.cycle()
  assert model.out == 9

#-----------------------------------------------------------------------
# ThreeStageTick
#-----------------------------------------------------------------------

class ThreeStageTick( Model ):
  def __init__( s, nbits ):
    s.nbits   = nbits
    s.in_     = InPort ( nbits )
    s.out     = OutPort( nbits )

  def elaborate_logic( s ):
    s.wire0   = Wire( s.nbits )

    @s.tick_rtl
    def func1():
      s.wire0.n = s.in_

    @s.tick_rtl
    def func2():
      s.out.n   = s.wire0

def test_ThreeStageTick( setup_sim ):
  pipeline_tester( setup_sim, ThreeStageTick( 16 ), 3 )

#-----------------------------------------------------------------------
# ThreeStagePosedge
#-----------------------------------------------------------------------

class ThreeStagePosedge( Model ):
  def __init__( s, nbits ):
    s.nbits   = nbits
    s.in_     = InPort ( nbits )
    s.out     = OutPort( nbits )

  def elaborate_logic( s ):
    s.wire0   = Wire( s.nbits )

    @s.posedge_clk
    def func1():
      s.wire0.n = s.in_

    @s.posedge_clk
    def func2():
      s.out.n   = s.wire0

def test_ThreeStagePosedge( setup_sim ):
  pipeline_tester( setup_sim, ThreeStagePosedge( 16 ), 3 )

#-----------------------------------------------------------------------
# FiveStageTick
#-----------------------------------------------------------------------

class FiveStageTick( Model ):
  def __init__( s, nbits ):
    s.nbits   = nbits
    s.in_     = InPort ( nbits )
    s.out     = OutPort( nbits )

  def elaborate_logic( s ):

    s.wire0   = Wire( s.nbits )

    @s.posedge_clk
    def func1():
      s.wire0.n = s.in_

    s.wire1   = Wire( s.nbits )

    @s.posedge_clk
    def func2():
      s.wire1.n = s.wire0

    s.wire2   = Wire( s.nbits )

    @s.posedge_clk
    def func3():
      s.wire2.n = s.wire1

    @s.posedge_clk
    def func4():
      s.out.n  = s.wire2

def test_FiveStageTick( setup_sim ):
  pipeline_tester( setup_sim, FiveStageTick( 16 ), 5 )

#-----------------------------------------------------------------------
# FiveStagePosedge
#-----------------------------------------------------------------------

class FiveStagePosedge( Model ):
  def __init__( s, nbits ):
    s.nbits   = nbits
    s.in_     = InPort ( nbits )
    s.out     = OutPort( nbits )

  def elaborate_logic( s ):

    s.wire0   = Wire( s.nbits )

    @s.posedge_clk
    def func1():
      s.wire0.n = s.in_

    s.wire1   = Wire( s.nbits )

    @s.posedge_clk
    def func2():
      s.wire1.n = s.wire0

    s.wire2   = Wire( s.nbits )

    @s.posedge_clk
    def func3():
      s.wire2.n = s.wire1

    @s.posedge_clk
    def func4():
      s.out.n  = s.wire2

def test_FiveStagePosedge( setup_sim ):
  pipeline_tester( setup_sim, FiveStagePosedge( 16 ), 5 )

#-----------------------------------------------------------------------
# NStagePosedge
#-----------------------------------------------------------------------

class NStageTick( Model ):
  def __init__( s, nbits, nstages ):
    s.nbits   = nbits
    s.nstages = nstages
    s.in_     = InPort ( nbits )
    s.out     = OutPort( nbits )

  def elaborate_logic( s ):

    s.wire = [ Wire( s.nbits ) for x in range( s.nstages ) ]

    s.connect( s.in_, s.wire[0]  )

    for i in range( s.nstages - 1 ):
      @s.tick_rtl
      def func( i = i ):  # Need to capture i for this to work
        s.wire[ i + 1 ].n = s.wire[ i ]

    s.connect( s.out, s.wire[-1] )


def test_NStageTick( setup_sim ):
  pipeline_tester( setup_sim, NStageTick( 16, 3 ), 3 )
  pipeline_tester( setup_sim, NStageTick( 16, 5 ), 5 )
  pipeline_tester( setup_sim, NStageTick( 16, 8 ), 8 )

#-----------------------------------------------------------------------
# NStagePosedge
#-----------------------------------------------------------------------

class NStagePosedge( Model ):
  def __init__( s, nbits, nstages ):
    s.nbits   = nbits
    s.nstages = nstages
    s.in_     = InPort ( nbits )
    s.out     = OutPort( nbits )

  def elaborate_logic( s ):

    s.wire = [ Wire( s.nbits ) for x in range( s.nstages ) ]

    s.connect( s.in_, s.wire[0]  )

    for i in range( s.nstages - 1 ):
      @s.posedge_clk
      def func( i = i ):  # Need to capture i for this to work
        s.wire[ i + 1 ].n = s.wire[ i ]

    s.connect( s.out, s.wire[-1] )


def test_NStagePosedge( setup_sim ):
  pipeline_tester( setup_sim, NStagePosedge( 16, 3 ), 3 )
  pipeline_tester( setup_sim, NStagePosedge( 16, 5 ), 5 )
  pipeline_tester( setup_sim, NStagePosedge( 16, 8 ), 8 )

#-----------------------------------------------------------------------
# NStageComb
#-----------------------------------------------------------------------
# TODO: THIS MODEL CURRENTLY CAUSES AN INFINITE LOOP IN PYTHON DUE TO THE
#       WAY WE DETECT SENSITIVITY LISTS... all wires/ports in an array
#       are added to the sensitivity list of an @combinational block since
#       we aren't sure of the value of i when walking the AST.
#
# UPDATE: FIXED!

class NStageComb( Model ):
  def __init__( s, nbits, nstages ):
    s.nbits   = nbits
    s.nstages = nstages
    s.in_     = InPort ( nbits )
    s.out     = OutPort( nbits )

  def elaborate_logic( s ):

    s.wire = [ Wire( s.nbits ) for x in range( s.nstages ) ]

    s.connect( s.in_, s.wire[0]  )

    for i in range( s.nstages - 1 ):
      @s.combinational
      def func( i = i ):  # Need to capture i for this to work
        s.wire[ i + 1 ].v = s.wire[ i ]

    s.connect( s.out, s.wire[-1] )

def test_NStageComb( setup_sim ):
  model      = NStageComb( 16, 3 )
  model, sim = setup_sim( model )
  # fill up the pipeline
  for i in range( 10 ):
    model.in_.v = i
    expected = ( i - 1 ) if ( i - 1 ) >= 0 else 0
    assert model.out == expected
    #assert False  # Prevent infinite loop!
    sim.cycle()

#-----------------------------------------------------------------------
# TempReadWrite
#-----------------------------------------------------------------------
# TODO: THIS MODEL CURRENTLY CAUSES AN INFINITE LOOP IN PYTHON DUE TO
#       THE WAY WE DETECT SENSITIVITY LISTS... all wires/ports read in
#       an @combinational block are added to the sensitivity list, if a
#       signal is written in the block and then read later in the block,
#       it repeatedly gets added to the event queue.  These 'temporary'
#       signals should really not be added to the sensitivity list. Fix.
#
# UPDATE: FIXED!
def test_WriteThenReadWire( setup_sim ):

  class WriteThenReadWire( Model ):
    def __init__( s, nbits ):
      s.in_     = InPort ( nbits )
      s.out     = OutPort( nbits )
      s.temp    = Wire   ( nbits )
      @s.combinational
      def comb_logic():
        s.temp.v = s.in_
        s.out.v  = s.temp
    # Temporary workaround
    #@s.combinational
    #def comb_logic():
    #  s.temp.v = s.in_
    #@s.combinational
    #def comb_logic():
    #  s.out.v  = s.temp

  model      = WriteThenReadWire( 16 )
  model, sim = setup_sim( model )
  for i in range( 10 ):
    model.in_.v = i
    #assert False  # Prevent infinite loop!
    sim.eval_combinational()
    assert model.out == i


#-----------------------------------------------------------------------
# BitsSensitivityListBugStore
#-----------------------------------------------------------------------
# Test to trigger bug where a Bits object is written to.
def test_BitsSensitivityListBugStore( setup_sim ):

  class Temp( Model ):
    def __init__( s, nbits ):
      s.in_  = InPort ( nbits )
      s.out  = OutPort( nbits )
      s.a    = Bits   ( nbits )
      @s.combinational
      def comb_logic():
        s.a         = s.in_
        s.out.value = s.in_
    def line_trace( s ):
      return '{} ({}) {}'.format( s.in_, s.a, s.out )

  model      = Temp( 16 )
  model, sim = setup_sim( model )
  # fill up the pipeline
  for i in range( 10 ):
    model.in_.value  = i
    sim.cycle()
    assert model.out == i

#-----------------------------------------------------------------------
# BitsSensitivityListBugLoad
#-----------------------------------------------------------------------
# Test to trigger bug where a Bits object is read from.
@pytest.mark.xfail
def test_BitsSensitivityListBugLoad( setup_sim ):

  class Temp( Model ):
    def __init__( s, nbits ):
      s.in_  = InPort ( nbits )
      s.out  = OutPort( nbits )
      s.out2 = OutPort( nbits )
      s.b    = Bits   ( nbits, 5 )
      @s.combinational
      def comb_logic():
        s.out .value = s.in_
        s.out2.value = s.b
    def line_trace( s ):
      return '{} ({}) {}'.format( s.in_, s.a, s.out )

  model      = Temp( 16 )
  model, sim = setup_sim( model )
  # fill up the pipeline
  for i in range( 10 ):
    model.in_.value  = i
    sim.cycle()
    assert model.out  == i
    assert model.out2 == 5
