#=========================================================================
# SimulationTool_wire_test.py
#=========================================================================
# Tests using wires for the SimulationTool class.

from pymtl import *

import pytest

#-------------------------------------------------------------------------
# Setup Sim
#-------------------------------------------------------------------------

def setup_sim( model ):
  model.elaborate()
  sim = SimulationTool( model )
  return sim

#-------------------------------------------------------------------------
# Pipeline Tester
#-------------------------------------------------------------------------

def pipeline_tester( model, nstages ):
  sim = setup_sim( model )
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

#-------------------------------------------------------------------------
# ThreeStageTick
#-------------------------------------------------------------------------

class ThreeStageTick( Model ):
  def __init__( s, nbits ):
    s.nbits   = nbits
    s.in_     = InPort ( nbits )
    s.out     = OutPort( nbits )

  def elaborate_logic( s ):
    s.wire0   = Wire( s.nbits )

    @s.tick
    def func1():
      s.wire0.n = s.in_

    @s.tick
    def func2():
      s.out.n   = s.wire0

def test_ThreeStageTick():
  pipeline_tester( ThreeStageTick( 16 ), 3 )

#-------------------------------------------------------------------------
# ThreeStagePosedge
#-------------------------------------------------------------------------

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

def test_ThreeStagePosedge():
  pipeline_tester( ThreeStagePosedge( 16 ), 3 )

#-------------------------------------------------------------------------
# FiveStageTick
#-------------------------------------------------------------------------

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

def test_FiveStageTick():
  pipeline_tester( FiveStageTick( 16 ), 5 )

#-------------------------------------------------------------------------
# FiveStagePosedge
#-------------------------------------------------------------------------

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

def test_FiveStagePosedge():
  pipeline_tester( FiveStagePosedge( 16 ), 5 )

#-------------------------------------------------------------------------
# NStagePosedge
#-------------------------------------------------------------------------

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
      @s.tick
      def func( i = i ):  # Need to capture i for this to work
        s.wire[ i + 1 ].n = s.wire[ i ]

    s.connect( s.out, s.wire[-1] )


def test_NStageTick():
  pipeline_tester( NStageTick( 16, 3 ), 3 )
  pipeline_tester( NStageTick( 16, 5 ), 5 )
  pipeline_tester( NStageTick( 16, 8 ), 8 )

#-------------------------------------------------------------------------
# NStagePosedge
#-------------------------------------------------------------------------

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


def test_NStagePosedge():
  pipeline_tester( NStagePosedge( 16, 3 ), 3 )
  pipeline_tester( NStagePosedge( 16, 5 ), 5 )
  pipeline_tester( NStagePosedge( 16, 8 ), 8 )

#-------------------------------------------------------------------------
# NStageComb
#-------------------------------------------------------------------------
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

def test_NStageComb():
  model = NStageComb( 16, 3 )
  sim   = setup_sim( model )
  # fill up the pipeline
  for i in range( 10 ):
    model.in_.v = i
    expected = ( i - 1 ) if ( i - 1 ) >= 0 else 0
    assert model.out == expected
    #assert False  # Prevent infinite loop!
    sim.cycle()

#-------------------------------------------------------------------------
# TempReadWrite
#-------------------------------------------------------------------------
# TODO: THIS MODEL CURRENTLY CAUSES AN INFINITE LOOP IN PYTHON DUE TO THE
#       WAY WE DETECT SENSITIVITY LISTS... all wires/ports read in an
#       @combinational block are added to the sensitivity list, if a
#       signal is written in the block and then read later in the block,
#       it repeatedly gets added to the event queue.  These 'temporary'
#       signals should really not be added to the sensitivity list. Fix.
#
# UPDATE: FIXED!

class WriteThenReadWire( Model ):
  def __init__( s, nbits ):
    s.nbits   = nbits
    s.in_     = InPort ( nbits )
    s.out     = OutPort( nbits )

  def elaborate_logic( s ):

    s.temp = Wire( s.nbits )

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

def test_WriteThenReadWire():
  model = WriteThenReadWire( 16 )
  sim = setup_sim( model )
  for i in range( 10 ):
    model.in_.v = i
    #assert False  # Prevent infinite loop!
    sim.eval_combinational()
    assert model.out == i


