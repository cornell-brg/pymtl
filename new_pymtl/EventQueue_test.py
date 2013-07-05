#=========================================================================
# EventQueue_test.py
#=========================================================================
# Tests for the C++ event queue.

from Model          import *
from SimulationTool import SimulationTool
from Bits           import Bits
from EventQueue     import new_cpp_queue, cpp_callback

from StringIO       import StringIO

#=========================================================================
# Basic Tests
#=========================================================================

#-------------------------------------------------------------------------
# BasicFuncCppQ
#-------------------------------------------------------------------------

var = 0

def test_BasicFuncCppQ():

  global var

  # Function Updating Global State

  def my_func():
    global var
    # Only works if var is global
    var += 2

  # Creating an FFI Callback

  cb = cpp_callback( my_func )
  cpp_queue = new_cpp_queue()

  # Enq

  assert cpp_queue.len() == 0
  cpp_queue.enq( cb, 0 )
  assert cpp_queue.len() == 1

  # Deq

  #func = cpp_queue.eval()
  func = cpp_queue.deq()
  assert cpp_queue.len() == 0

  # Call Function

  func()
  assert var == 2

  # Many Enq

  for i in range( 5 ):
    cpp_queue.enq( cb, 0 )

  # Many Deq

  i = var
  while cpp_queue.len():
    #func = cpp_queue.eval()
    func = cpp_queue.deq()
    func()
    assert var == i + 2
    i += 2


#=========================================================================
# Class With Registered Function Tests
#=========================================================================

#-------------------------------------------------------------------------
# Registered Function Dummy Class
#-------------------------------------------------------------------------

# Data Wrapper storing state

class Port( object ):
  def __init__( self ):
    self.data = 0

# Example Class

class Example( object ):

  # Constructor with function list

  def __init__( self ):
    self._funcs = []
    self.in_    = Port()
    self.out    = Port()

  # Method for declaring and update functions

  def setup( self ):

    # Inner function is registered and stored by the class
    @self.register
    def logic():
      self.out.data = self.in_.data

  # Decorator for registering update functions with the class

  def register( self, func ):
    self._funcs.append( func )
    return func

#-------------------------------------------------------------------------
# RegisteredFuncPythonQ
#-------------------------------------------------------------------------

def test_RegisteredFuncPythonQ():

  ex = Example()
  ex.setup()

  # Single Write
  ex.in_.data = 5
  assert ex.out.data == 0
  fp = ex._funcs[0]
  fp()
  #print ex.out.data
  assert ex.out.data == 5

  # Series of Writes
  for i in range( 10 ):
    ex.in_.data = i
    fp = ex._funcs[0]
    fp()
    #print ex.out.data
    assert ex.out.data == i

#-------------------------------------------------------------------------
# RegisteredFuncCppQ
#-------------------------------------------------------------------------

def test_RegisteredFuncCppQ():

  ex = Example()
  ex.setup()

  cpp_queue = new_cpp_queue()

  # Single Write
  ex.in_.data = 5
  assert ex.out.data == 0
  # Create callback, enq, deq, call
  cb = cpp_callback( ex._funcs[0] )
  cpp_queue.enq( cb, 0 )
  #cp = cpp_queue.eval()
  cp = cpp_queue.deq()
  cp()
  #print ex.out.data
  assert ex.out.data == 5

  # Series of Writes
  for i in range( 10 ):
    ex.in_.data = i
    cb = cpp_callback( ex._funcs[0] )
    cpp_queue.enq( cb, 0 )
    #cp = cpp_queue.eval()
    cp = cpp_queue.deq()
    cp()
    #print ex.out.data
    assert ex.out.data == i

#=========================================================================
# PyMTL Model Tests
#=========================================================================

#-------------------------------------------------------------------------
# PassThrough
#-------------------------------------------------------------------------

class PassThrough( Model ):
  def __init__( s, nbits ):
    s.in_ = InPort ( nbits )
    s.out = OutPort( nbits )

  def elaborate_logic( s ):
    @s.combinational
    def logic():
      s.out.v = s.in_

#-------------------------------------------------------------------------
# ModelDummyQ
#-------------------------------------------------------------------------

def test_ModelDummyQ():
  model = PassThrough( 8 )
  model.elaborate()

  # Hacky SimulationTool mocking
  model.in_ = Bits( 8 )
  model.out = Bits( 8 )

  func = model._combinational_blocks[0]

  def set_eval_check( value ):
    model.in_.v = value
    func()
    assert model.out == value

  for i in range( 0, 100, 15 ):
    set_eval_check( i )

#-------------------------------------------------------------------------
# ModelCPPQueue
#-------------------------------------------------------------------------

def test_CPPQueue():
  model = PassThrough( 8 )
  model.elaborate()

  # Hacky SimulationTool mocking
  model.in_ = Bits( 8 )
  model.out = Bits( 8 )

  fp = model._combinational_blocks[0]
  cpp_queue = new_cpp_queue()
  fp.cb = cpp_callback( fp )

  def set_eval_check( value ):
    model.in_.v = value
    cpp_queue.enq( fp.cb, 0 )
    #cp = cpp_queue.eval()
    cp = cpp_queue.deq()
    cp()
    assert model.out == value

  assert cpp_queue.len() == 0

  for i in range( 0, 100, 15 ):
    set_eval_check( i )

#-------------------------------------------------------------------------
# ModelSimQ
#-------------------------------------------------------------------------
# Simple integration test (assuming SimulationTool has been modified to
# use the cpp_queue).

def test_ModelSimQ():
  model = PassThrough( 8 )
  model.elaborate()
  sim   = SimulationTool( model )

  def set_eval_check( value ):
    model.in_.v = value
    sim.eval_combinational()
    assert model.out == value

  for i in range( 0, 100, 15 ):
    set_eval_check( i )

#=========================================================================
# PyMTL Redundant Eval Test
#=========================================================================

#-------------------------------------------------------------------------
# Adder
#-------------------------------------------------------------------------

class Adder( Model ):
  def __init__( s, nbits ):
    s.a   = InPort ( nbits )
    s.b   = InPort ( nbits )
    s.out = OutPort( nbits )

  def elaborate_logic( s ):
    @s.combinational
    def logic():
      s.out.v = s.a + s.b

#-------------------------------------------------------------------------
# ModelSimQ
#-------------------------------------------------------------------------

def test_ModelSimQRedundant():
  model = Adder( 8 )
  model.elaborate()
  sim   = SimulationTool( model )

  # Test of basic functionality

  model.a.v = 1
  model.b.v = 2
  sim.cycle()
  assert model.out == 3

  # Testing Event queue membership, want eval only added to queue once!

  model.a.v = 5
  assert len( sim._event_queue ) == 1

  # If value doesn't change, dont add it to the queue
  model.a.v = 5
  assert len( sim._event_queue ) == 1

  # If event already in queue, don't add it again
  model.b.v = 3
  assert len( sim._event_queue ) == 1

  model.b.v = 5
  assert len( sim._event_queue ) == 1

  sim.cycle()
  assert model.out == 10

  assert len( sim._event_queue ) == 0

