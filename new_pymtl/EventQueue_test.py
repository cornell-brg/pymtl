#=========================================================================
# EventQueue_test.py
#=========================================================================
# Tests for the C++ event queue.

from Model          import *
from SimulationTool import SimulationTool
from Bits           import Bits
from EventQueue     import cpp_queue, cpp_callback

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

  # Enq

  assert cpp_queue.len() == 0
  cpp_queue.enq( cb )
  assert cpp_queue.len() == 1

  # Deq

  func = cpp_queue.deq()
  assert cpp_queue.len() == 0

  # Call Function

  func()
  assert var == 2

  # Many Enq

  for i in range( 5 ):
    cpp_queue.enq( cb )

  # Many Deq

  i = var
  while cpp_queue.len():
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

  # Single Write
  ex.in_.data = 5
  assert ex.out.data == 0
  # Create callback, enq, deq, call
  cb = cpp_callback( ex._funcs[0] )
  cpp_queue.enq( cb )
  cp = cpp_queue.deq()
  cp()
  #print ex.out.data
  assert ex.out.data == 5

  # Series of Writes
  for i in range( 10 ):
    ex.in_.data = i
    cb = cpp_callback( ex._funcs[0] )
    cpp_queue.enq( cb )
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

  def set_eval_check( value ):
    model.in_.v = value
    cb = cpp_callback( fp )
    cpp_queue.enq( cb )
    cp = cpp_queue.deq()
    cp()
    assert model.out == value

  assert cpp_queue.len() == 0

  for i in range( 0, 100, 15 ):
    set_eval_check( i )

#-------------------------------------------------------------------------
# ModelSimQ
#-------------------------------------------------------------------------
# For now this tests the python collections.deque, but once the C++
# EventQueue implementation is integrated into the SimulationTool, this
# will be a simple integration test.

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
