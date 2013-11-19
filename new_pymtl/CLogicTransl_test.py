#=========================================================================
# VerilogLogicTransl_test.py
#=========================================================================

import SimulationTool_seq_test    as sequential
import SimulationTool_struct_test as structural

from CLogicTransl import CLogicTransl
from subprocess   import check_output, STDOUT, CalledProcessError
from SignalValue  import CreateWrappedClass
from Model        import *

from CLogicHelpers import gen_cppsim

import tempfile
import os

compiler = "g++ -O3 -fPIC -shared -o {libname} {csource}"

#-------------------------------------------------------------------------
# translate
#-------------------------------------------------------------------------
def translate( model ):
  model.elaborate()

  with tempfile.NamedTemporaryFile(suffix='.cpp') as output:

    cdef, CSimWrapper = CLogicTransl( model, output )
    output.flush()

    # NOTE: if we don't create a unique name for each .so, things get
    #       inconsisten (stale data?)
    clib = os.getcwd() + '/' + model.class_name+'.so'
    cmd  = compiler.format( libname = clib,
                            csource = output.name )

    try:

      result = check_output( cmd.split() , stderr=STDOUT )
      output.seek(0)
      source = output.read()

      csim, ffi = gen_cppsim ( clib, cdef )
      sim       = CSimWrapper( csim, ffi )

      print
      print source
      #print

      return sim

    except CalledProcessError as e:

      output.seek(0)
      source = output.read()

      raise Exception( 'Module did not compile!\n\n'
                       'Command:\n' + ' '.join(e.cmd) + '\n\n'
                       'Error:\n' + e.output + '\n'
                       'Source:\n \x1b[31m' + source + '\x1b[0m'
                     )


#-------------------------------------------------------------------------
# NetObject
#-------------------------------------------------------------------------
class _NetObject( object ):
  def __init__( self, dest=0, src=0, seqnum=0, payload=0 ):
    self.dest    = dest
    self.src     = src
    self.seqnum  = seqnum
    self.payload = payload

NO = CreateWrappedClass( _NetObject )

#-------------------------------------------------------------------------
# Sequential Logic
#-------------------------------------------------------------------------

def test_Register():
  sim = translate( sequential.Register( 8 ) )
  sim.in_ = 8; assert sim.out == 0
  sim.cycle(); assert sim.out == 8
  sim.in_ = 9; assert sim.out == 8
  sim.in_ = 10
  sim.cycle(); assert sim.out == 10
  sim.in_ = 2
  sim.cycle(); assert sim.out == 2

def test_RegisterWrapped():
  sim = translate( sequential.RegisterWrapped( 8 ) )
  sim.in_ = 8; assert sim.out == 0
  sim.cycle(); assert sim.out == 8
  sim.in_ = 9; assert sim.out == 8
  sim.in_ = 10
  sim.cycle(); assert sim.out == 10
  sim.in_ = 2
  sim.cycle(); assert sim.out == 2

def test_RegisterWrappedChain():
  sim = translate( sequential.RegisterWrappedChain( 8 ) )
  sim.in_ = 8; assert sim.out == 0
  sim.cycle(); assert sim.out == 0
  sim.cycle(); assert sim.out == 0
  sim.in_ = 9;
  sim.in_ = 10
  sim.cycle(); assert sim.out == 8
  sim.in_ = 2
  sim.cycle(); assert sim.out == 8
  sim.cycle(); assert sim.out == 10
  sim.cycle(); assert sim.out == 2

def test_RegisterReset():
  sim = translate( sequential.RegisterReset( 16 ) )
  model = sim
  model.in_ = 8
  assert model.out == 0
  sim.reset()
  assert model.out == 0
  sim.cycle()
  assert model.out == 8
  model.in_ = 9
  assert model.out == 8
  model.in_ = 10
  sim.cycle()
  assert model.out == 10
  sim.reset()
  assert model.out == 0

# TODO: slices not supported
# TODO: bit math doesn't work properly

#def test_SliceWriteCheck():
#  translate( sequential.SliceWriteCheck( 16 ) )
#
#def test_SliceTempWriteCheck():
#  translate( sequential.SliceTempWriteCheck( 16 ) )

def test_MultipleWrites():
  sim = translate( sequential.MultipleWrites() )
  model = sim

  assert model.out == 0
  sim.cycle(); assert model.out == 1
  sim.cycle(); assert model.out == 1
  sim.cycle(); assert model.out == 1

#-------------------------------------------------------------------------
# Complex Objects
#-------------------------------------------------------------------------
#def test_Register_Obj():
#  translate( sequential.Register( NO ) )

#-------------------------------------------------------------------------
# Structural
#-------------------------------------------------------------------------

def passthrough_tester( model ):
  model.in_ = 8
  # Note: no need to call cycle, no @combinational block
  # TODO: must call cycle with current impl, change later!
  model.cycle()  # TODO: remove
  assert model.out   == 8
  model.in_ = 9
  model.in_ = 10
  model.cycle()  # TODO: remove
  assert model.out == 10

def test_PassThrough():
  passthrough_tester( translate( structural.PassThrough(8) ) )

def test_PassThroughWrapped():
  passthrough_tester( translate( structural.PassThroughWrapped(8) ) )

def test_PassThroughWrappedChain():
  passthrough_tester( translate( structural.PassThroughWrappedChain(8) ) )

def splitter_tester( model ):
  model.in_ = 8
  model.cycle()  # TODO: remove
  assert model.out0 == 8
  model.cycle()  # TODO: remove
  assert model.out1 == 8
  model.in_ = 9
  model.in_ = 10
  model.cycle()  # TODO: remove
  assert model.out0 == 10
  assert model.out1 == 10

def test_Splitter():
  splitter_tester( translate(structural.Splitter(16)) )

def test_SplitterWires():
  splitter_tester( translate(structural.SplitterWires(16)) )

def test_SplitterWrapped():
  splitter_tester( translate(structural.SplitterWrapped(16)) )

def test_SplitterPT_1():
  splitter_tester( translate(structural.SplitterPT_1(16)) )

def test_SplitterPT_2():
  splitter_tester( translate(structural.SplitterPT_2(16)) )

def test_SplitterPT_3():
  splitter_tester( translate(structural.SplitterPT_3(16)) )

def test_SplitterPT_4():
  splitter_tester( translate(structural.SplitterPT_4(16)) )

def test_SplitterPT_5():
  splitter_tester( translate(structural.SplitterPT_5(16)) )

def test_PassThroughList():
  sim = translate( structural.PassThroughList(16, 4) )
  model = sim
  for i in range( 4 ):
    model.in_[i] = i
  model.cycle()  # TODO: remove
  for i in range( 4 ):
    # Note: no need to call cycle, no @combinational block
    assert model.out[i] == i
  model.in_[2] = 9
  model.in_[2] = 10
  model.cycle()  # TODO: remove
  assert model.out[2] == 10

def test_PassThroughListWire():
  sim = translate( structural.PassThroughListWire(16, 4) )
  model = sim
  for i in range( 4 ):
    model.in_[i] = i
  model.cycle()  # TODO: remove
  for i in range( 4 ):
    # Note: no need to call cycle, no @combinational block
    assert model.out[i] == i
  model.in_[2] = 9
  model.in_[2] = 10
  model.cycle()  # TODO: remove
  assert model.out[2] == 10


#-------------------------------------------------------------------------
# Sequential
#-------------------------------------------------------------------------
def for_tester( model ):
  sim = translate( model )
  model = sim
  for i in range( 4 ): model.in_[i] = i
  model.cycle()
  for i in range( 4 ): assert model.out[i] == i
  model.in_[2] = 9
  model.in_[2] = 10
  model.cycle()
  assert model.out[2] == 10

class ForAssign0( Model ):
  def __init__( s ):
    s.in_ = [ InPort (16) for x in range(4) ]
    s.out = [ OutPort(16) for x in range(4) ]
    s.nports = 4
  def elaborate_logic( s ):
    @s.posedge_clk
    def logic():
      for i in range( s.nports ):
        s.out[i].next = s.in_[i]

def test_ForAssign0():
  for_tester( ForAssign0() )

# TODO
#class ForAssign1( Model ):
#  def __init__( s ):
#    s.in_ = [ InPort (16) for x in range(4) ]
#    s.out = [ OutPort(16) for x in range(4) ]
#  def elaborate_logic( s ):
#    @s.posedge_clk
#    def logic():
#      for i in range( len( s.in_ ) ):
#        s.out[i].next = s.in_[i]
#
#def test_ForAssign1():
#  for_tester( ForAssign1() )

# TODO
#class ForAssign2( Model ):
#  def __init__( s ):
#    s.in_ = [ InPort (16) for x in range(4) ]
#    s.out = [ OutPort(16) for x in range(4) ]
#  def elaborate_logic( s ):
#    @s.posedge_clk
#    def logic():
#      i = 0
#      for input in s.in_:
#        s.out[i].next = input
#        i += 1
#
#def test_ForAssign2():
#  for_tester( ForAssign1() )

# TODO
#class ForAssign3( Model ):
#  def __init__( s ):
#    s.in_ = [ InPort (16) for x in range(4) ]
#    s.out = [ OutPort(16) for x in range(4) ]
#  def elaborate_logic( s ):
#    @s.posedge_clk
#    def logic():
#      for i, input in enumerate( s.in_ ):
#        s.out[i].next = input
#
#def test_ForAssign3():
#  for_tester( ForAssign1() )

#-------------------------------------------------------------------------
# PortBundles
#-------------------------------------------------------------------------
from new_pmlib        import InValRdyBundle, OutValRdyBundle
class TestValRdy0( Model ):
  def __init__( s ):
    s.in_ = InValRdyBundle (16)
    s.out = OutValRdyBundle(16)
  def elaborate_logic( s ):
    s.connect( s.in_, s.out )

def test_TestValRdy0():
  sim = translate( TestValRdy0() )
  sim.in__msg = 9
  sim.in__val = 1
  sim.out_rdy = 1
  sim.cycle()
  assert sim.out_msg == 9
  assert sim.out_val == 1
  assert sim.in__rdy == 1
  sim.in__msg = 7
  sim.in__val = 0
  sim.out_rdy = 1
  sim.cycle()
  assert sim.out_msg == 7
  assert sim.out_val == 0
  assert sim.in__rdy == 1

class TestValRdy1( Model ):
  def __init__( s ):
    s.in_ = InValRdyBundle (16)
    s.out = OutValRdyBundle(16)
  def elaborate_logic( s ):
    @s.tick
    def logic():
      s.out.msg.next = s.in_.msg
      s.out.val.next = s.in_.val
      s.in_.rdy.next = s.out.rdy

def test_TestValRdy1():
  sim = translate( TestValRdy0() )
  sim.in__msg = 9
  sim.in__val = 1
  sim.out_rdy = 1
  sim.cycle()
  assert sim.out_msg == 9
  assert sim.out_val == 1
  assert sim.in__rdy == 1
  sim.in__msg = 7
  sim.in__val = 0
  sim.out_rdy = 1
  sim.cycle()
  assert sim.out_msg == 7
  assert sim.out_val == 0
  assert sim.in__rdy == 1

class TestValRdy2( Model ):
  def __init__( s ):
    s.in_ = [ InValRdyBundle (16) for x in range(2) ]
    s.out = [ OutValRdyBundle(16) for x in range(2) ]
  def elaborate_logic( s ):
    for i, o in zip( s.in_, s.out ):
      s.connect( i, o )

def valrdyarray_test( model ):
  sim = translate( model )
  sim.in__msg[0] = 9
  sim.in__val[0] = 1
  sim.out_rdy[0] = 1
  sim.in__msg[1] = 8
  sim.in__val[1] = 1
  sim.out_rdy[1] = 1
  sim.cycle()
  assert sim.out_msg[0] == 9
  assert sim.out_val[0] == 1
  assert sim.in__rdy[0] == 1
  assert sim.out_msg[1] == 8
  assert sim.out_val[1] == 1
  assert sim.in__rdy[1] == 1
  sim.in__msg[0] = 7
  sim.in__val[0] = 0
  sim.out_rdy[0] = 1
  sim.cycle()
  assert sim.out_msg[0] == 7
  assert sim.out_val[0] == 0
  assert sim.in__rdy[0] == 1

def test_TestValRdy2():
  valrdyarray_test( TestValRdy2() )

class TestValRdy3( Model ):
  def __init__( s ):
    s.in_ = [ InValRdyBundle (16) for x in range(2) ]
    s.out = [ OutValRdyBundle(16) for x in range(2) ]
  def elaborate_logic( s ):
    @s.tick
    def logic():
      s.out[0].msg.next = s.in_[0].msg
      s.out[0].val.next = s.in_[0].val
      s.in_[0].rdy.next = s.out[0].rdy
      s.out[1].msg.next = s.in_[1].msg
      s.out[1].val.next = s.in_[1].val
      s.in_[1].rdy.next = s.out[1].rdy

def test_TestValRdy3():
  valrdyarray_test( TestValRdy3() )

class TestValRdy4( Model ):
  def __init__( s, nports ):
    s.nports = nports
    s.in_ = [ InValRdyBundle (16) for x in range(nports) ]
    s.out = [ OutValRdyBundle(16) for x in range(nports) ]
  def elaborate_logic( s ):
    @s.tick
    def logic():
      for i in range( s.nports ):
        s.out[i].msg.next = s.in_[i].msg
        s.out[i].val.next = s.in_[i].val
        s.in_[i].rdy.next = s.out[i].rdy
def test_TestValRdy4():
  valrdyarray_test( TestValRdy4(2) )


#-------------------------------------------------------------------------
# ValRdyQueues
#-------------------------------------------------------------------------
#from new_pmlib.queues import InValRdyQueue, OutValRdyQueue
#
#class IVQueue( Model ):
#  def __init__( s ):
#    s.in_ = InValRdyBundle(16)
#    s.out = OutPort (16)
#    s.chk = OutPort (16)
#  def elaborate_logic( s ):
#    s.inbuf = InValRdyQueue( 16, 2 )
#    s.connect( s.in_, s.inbuf.in_ )
#    @s.posedge_clk
#
#    def logic():
#      s.inbuf.xtick()
#      if not s.inbuf.is_empty():
#        s.chk.next = s.inbuf.peek() == 3
#        x = s.inbuf.deq()
#        s.out.next = x
#
#def test_IVQueue():
#  sim = translate( IVQueue() )
#  model = sim
#  model.in_.msg = 2
#  model.in_.val = 1
#  model.cycle()
#  assert model.chk == 0
#  assert model.out == 0
#  model.in_.msg = 3
#  model.in_.val = 1
#  assert model.chk == 0
#  assert model.out == 2
##  model.cycle()
##  assert model.chk == 1
##  assert model.out == 3
