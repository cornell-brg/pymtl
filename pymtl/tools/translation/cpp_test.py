#=========================================================================
# cpp_test.py
#=========================================================================

from pymtl       import *
from cpp         import CLogicTransl, compiler
from cpp_helpers import gen_cppsim
from subprocess  import check_output, STDOUT, CalledProcessError

import tempfile
import os

from ..simulation import SimulationTool_seq_test    as sequential
from ..simulation import SimulationTool_struct_test as structural

#-----------------------------------------------------------------------
# translate
#-----------------------------------------------------------------------
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

      #print
      #print source
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


#-----------------------------------------------------------------------
# NetObject
#-----------------------------------------------------------------------
class _NetObject( object ):
  def __init__( self, dest=0, src=0, seqnum=0, payload=0 ):
    self.dest    = dest
    self.src     = src
    self.seqnum  = seqnum
    self.payload = payload

NO = CreateWrappedClass( _NetObject )

#-----------------------------------------------------------------------
# Sequential Logic
#-----------------------------------------------------------------------

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

#-----------------------------------------------------------------------
# Complex Objects
#-----------------------------------------------------------------------
#def test_Register_Obj():
#  translate( sequential.Register( NO ) )

#-----------------------------------------------------------------------
# Structural
#-----------------------------------------------------------------------

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


#-----------------------------------------------------------------------
# Sequential
#-----------------------------------------------------------------------
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

#-----------------------------------------------------------------------
# ModuleListPortList
#-----------------------------------------------------------------------
class ModuleListPortList( Model ):
  def __init__( s ):
    s.in_ = [ InPort (16) for x in range(4) ]
    s.out = [ OutPort(16) for x in range(4) ]
    s.nports = 4
  def elaborate_logic( s ):
    s.mods = [ ForAssign0() for i in range(3) ]
    for i in range( 4 ):
      s.connect( s.in_[i],         s.mods[0].in_[i] )
      s.connect( s.mods[0].out[i], s.mods[1].in_[i] )
      s.connect( s.mods[1].out[i], s.mods[2].in_[i] )
      s.connect( s.mods[2].out[i], s.out[i]         )

def test_ModuleListPortList():
  s = translate( ModuleListPortList() )

  def put(exp):
    for i, j in enumerate( exp ): s.in_[i]  = j
  def check(exp):
    for i, j in enumerate( exp ): assert s.out[i] == j

  def debug():
    print "{:3}:".format(s.ncycles),
    for i in range(4): print s.out[i],
    print

  s.reset()
  put([1,2,3,4]); s.cycle(); debug();
  put([0,0,0,0]); s.cycle(); debug();
  put([0,0,0,0]); s.cycle(); debug(); check([1,2,3,4])
  put([0,0,0,0]); s.cycle(); debug();
  put([0,0,0,0]); s.cycle(); debug();
  put([0,0,0,0]); s.cycle(); debug();




#-----------------------------------------------------------------------
# PortBundles
#-----------------------------------------------------------------------
from pclib.ifaces import InValRdyBundle, OutValRdyBundle
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

#-----------------------------------------------------------------------
# Queues
#-----------------------------------------------------------------------
from pclib.cl import Queue
from copy     import copy

class TestQueue( Model ):
  def __init__( s ):
    s.in_ = InValRdyBundle (16)
    s.out = OutValRdyBundle(16)
  def elaborate_logic( s ):
    s.buf = Queue(2)
    @s.tick
    def logic():

      if s.out.rdy and s.out.val:
        s.buf.deq()
      if s.in_.rdy and s.in_.val:
        s.buf.enq( copy( s.in_.msg ) )

      if not s.buf.is_empty():
        s.out.msg.next = s.buf.peek()
      s.out.val.next = not s.buf.is_empty()
      s.in_.rdy.next = not s.buf.is_full()

def test_TestQueue():
  sim = translate( TestQueue() )
  sim.reset()
  sim.in__msg = 9
  sim.in__val = 1
  sim.out_rdy = 1
  sim.cycle() # enq 9
  assert sim.out_msg == 9
  assert sim.out_val == 1
  assert sim.in__rdy == 1
  sim.in__msg = 8
  sim.in__val = 1
  sim.out_rdy = 1
  sim.cycle() # enq 8, deq 9
  assert sim.out_msg == 8
  assert sim.out_val == 1
  assert sim.in__rdy == 1
  sim.in__msg = 7
  sim.in__val = 1
  sim.out_rdy = 0
  sim.cycle() # enq 7
  assert sim.out_msg == 8
  assert sim.out_val == 1
  assert sim.in__rdy == 0
  sim.in__msg = 6
  sim.in__val = 1
  sim.out_rdy = 1
  sim.cycle() # deq 8
  assert sim.out_msg == 7
  assert sim.out_val == 1
  assert sim.in__rdy == 1


class TestTwoQueue( Model ):
  def __init__( s ):
    s.in_ = InValRdyBundle (16)
    s.out = OutValRdyBundle(16)
  def elaborate_logic( s ):
    s.inbuf  = Queue(2)
    s.outbuf = Queue(2)
    s.data   = 0
    @s.tick
    def logic():

      if s.in_.rdy and s.in_.val:
        s.inbuf.enq( copy( s.in_.msg) )

      if s.out.rdy and s.out.val:
        s.outbuf.deq()

      if not s.outbuf.is_empty():
        s.out.msg.next = s.outbuf.peek()
      s.out.val.next = not s.outbuf.is_empty()
      s.in_.rdy.next = not s.inbuf.is_full()

      if not s.inbuf.is_empty() and not s.outbuf.is_full():
        s.data = s.inbuf.peek()
        s.outbuf.enq( s.data )
        s.inbuf.deq()

def test_TestTwoQueue():
  sim = translate( TestTwoQueue() )
  sim.reset()
  sim.in__msg = 9
  sim.in__val = 1
  sim.out_rdy = 1
  sim.cycle() # enq 9
  #assert sim.out_msg == 9
  assert sim.out_val == 0
  assert sim.in__rdy == 1
  sim.in__msg = 8
  sim.in__val = 1
  sim.out_rdy = 1
  sim.cycle() # enq 8, out 9
  assert sim.out_msg == 9
  assert sim.out_val == 1
  assert sim.in__rdy == 1
  sim.in__msg = 7
  sim.in__val = 1
  sim.out_rdy = 0
  sim.cycle() # enq 7, out 9
  assert sim.out_msg == 9
  assert sim.out_val == 1
  assert sim.in__rdy == 1
  sim.in__msg = 6
  sim.in__val = 1
  sim.out_rdy = 1
  sim.cycle() # enq 6, deq 9, out 8
  assert sim.out_msg == 8
  assert sim.out_val == 1
  assert sim.in__rdy == 0
  sim.in__val = 0
  sim.cycle() # deq 8, out 7
  assert sim.out_msg == 7
  assert sim.out_val == 1
  assert sim.in__rdy == 1
  sim.cycle() # deq 7, out 6
  assert sim.out_msg == 6
  assert sim.out_val == 1
  assert sim.in__rdy == 1
  sim.cycle() # deq 6
  assert sim.out_val == 0
  assert sim.in__rdy == 1

class TestTwoQueueList( Model ):
  def __init__( s ):
    s.in_ = [ InValRdyBundle (16) for x in range(2) ]
    s.out = [ OutValRdyBundle(16) for x in range(2) ]
  def elaborate_logic( s ):
    s.inbuf  = [ Queue(2) for x in range(2) ]
    s.outbuf = [ Queue(2) for x in range(2) ]
    s.data   = 0
    @s.tick
    def logic():

      for i in range(2):
        if s.in_[i].rdy and s.in_[i].val:
          s.inbuf[i].enq( copy( s.in_[i].msg) )

        if s.out[i].rdy and s.out[i].val:
          s.outbuf[i].deq()

      for i in range(2):
        if not s.outbuf[i].is_empty():
          s.out[i].msg.next = s.outbuf[i].peek()
        s.out[i].val.next = not s.outbuf[i].is_empty()
        s.in_[i].rdy.next = not s.inbuf[i].is_full()

      for i in range(2):
        if not s.inbuf[i].is_empty() and not s.outbuf[i].is_full():
          s.data = s.inbuf[i].peek()
          s.outbuf[i].enq( s.data )
          s.inbuf[i].deq()

def test_TestTwoQueueList():
  sim = translate( TestTwoQueueList() )
  sim.reset()
  for i in range( 2 ):
    sim.in__msg[i] = 9 + i
    sim.in__val[i] = 1
    sim.out_rdy[i] = 1
  sim.cycle() # enq 9
  #assert sim.out_msg == 9
  for i in range( 2 ):
    assert sim.out_val[i] == 0
    assert sim.in__rdy[i] == 1
    sim.in__msg[i] = 8 + i
    sim.in__val[i] = 1
    sim.out_rdy[i] = 1
  sim.cycle() # enq 8, out 9
  for i in range( 2 ):
    assert sim.out_msg[i] == 9+i
    assert sim.out_val[i] == 1
    assert sim.in__rdy[i] == 1
    sim.in__msg[i] = 7+i
    sim.in__val[i] = 1
    sim.out_rdy[i] = 0
  sim.cycle() # enq 7, out 9
  for i in range( 2 ):
    assert sim.out_msg[i] == 9+i
    assert sim.out_val[i] == 1
    assert sim.in__rdy[i] == 1
    sim.in__msg[i] = 6+i
    sim.in__val[i] = 1
    sim.out_rdy[i] = 1
  sim.cycle() # enq 6, deq 9, out 8
  for i in range( 2 ):
    assert sim.out_msg[i] == 8+i
    assert sim.out_val[i] == 1
    assert sim.in__rdy[i] == 0
    sim.in__val[i] = 0
  sim.cycle() # deq 8, out 7
  for i in range( 2 ):
    assert sim.out_msg[i] == 7+i
    assert sim.out_val[i] == 1
    assert sim.in__rdy[i] == 1

#-----------------------------------------------------------------------
# Function Call
#-----------------------------------------------------------------------
from math import sqrt
class FunctionCall0( Model ):
  NORTH = 0
  EAST  = 1
  SOUTH = 2
  WEST  = 3
  TERM  = 4
  def __init__( s, id_, nrouters ):
    s.id_       = id_
    s.xnodes    = int( sqrt( nrouters ) )
    s.x         = id_ % s.xnodes
    s.y         = id_ / s.xnodes
    s.in_ = InPort ( 8 )
    s.out = OutPort( 8 )
    s.x_dest = 0
    s.y_dest = 0

  def elaborate_logic( s ):
    s.temp = 0
    @s.tick
    def logic():
      s.temp = s.route_compute( s.in_ )
      s.out.next = s.temp

  # TODO: hacky, fix later!
  def route_compute( s=0, dest=0 ):
    s.x_dest = dest % s.xnodes
    s.y_dest = dest / s.xnodes
    if   s.x_dest < s.x: return s.WEST
    elif s.x_dest > s.x: return s.EAST
    elif s.y_dest < s.y: return s.NORTH
    elif s.y_dest > s.y: return s.SOUTH
    else:
      assert s.x_dest == s.x
      assert s.y_dest == s.y
      return s.TERM

def test_FunctionCall0():
  F = FunctionCall0
  s = translate( FunctionCall0( 10, 16) )
  s.reset()
  s.in_ = 10; s.cycle(); assert s.out == F.TERM
  s.in_ =  8; s.cycle(); assert s.out == F.WEST
  s.in_ =  2; s.cycle(); assert s.out == F.NORTH
  s.in_ = 14; s.cycle(); assert s.out == F.SOUTH
  s.in_ = 11; s.cycle(); assert s.out == F.EAST

# TODO: only one of these works at a time... wtf
#def test_FunctionCall1():
#  F = FunctionCall0
#  s = translate( FunctionCall0( 1, 4) )
#  s.reset()
#  s.in_ = 0; s.cycle();  assert s.out == F.WEST
#  s.in_ = 1; s.cycle();  assert s.out == F.TERM
#  s.in_ = 2; s.cycle();  assert s.out == F.WEST
#  s.in_ = 3; s.cycle();  assert s.out == F.SOUTH

class FunctionCall1( Model ):
  NORTH = 0
  EAST  = 1
  SOUTH = 2
  WEST  = 3
  TERM  = 4

  def __init__( s, offset, dummy ):
    s.in_  = [ InPort ( 8 ) for x in range( 5 ) ]
    s.outd = [ OutPort( 8 ) for x in range( 5 ) ]
    s.outw = [ OutPort( 8 ) for x in range( 5 ) ]

    s.offset     = offset
    s.priorities = [0]*5
    s.winners    = [0]*5
    s.temp       = 0

    s.i          = 0
    s.last       = 0
    s.enter      = 0

  def elaborate_logic( s ):
    s.temp = 0
    @s.tick
    def logic():

      for i in range( 5 ):
        s.temp         = s.arbitrate( i )
        s.outd[i].next = s.temp

      for i in range( 5 ):
        s.outw[i].next = s.priorities[i]

  def arbitrate( s=0, output=0 ):
    s.i     = s.priorities[output]
    s.last  = s.i
    s.enter = 0
    while not (s.i == s.last and s.enter):
      s.enter = 1
      if s.route_compute( s.in_[s.i] ) == output:
        s.priorities[ output ] = ( s.i + 1 ) % 5
        s.winners[ output ] = 1
        return s.i
      s.i = (s.i + 1) % 5
    s.winners[ output ] = 0
    # No winner
    return 0xFF

  def route_compute( s=0, dest=0 ):
     return (dest + s.offset) % 5

def test_FunctionCall1():
  F = FunctionCall1
  s = translate( F( 1, 0) )
  s.reset()
  for i in range(5):
    s.in_[i] = i
  s.cycle()
  assert s.outd[0] == 4
  assert s.outd[1] == 0
  assert s.outd[2] == 1
  assert s.outd[3] == 2
  assert s.outd[4] == 3
  assert s.outw[0] == 0
  assert s.outw[1] == 1
  assert s.outw[2] == 2
  assert s.outw[3] == 3
  assert s.outw[4] == 4
  for i in range(5):
    s.in_[i] = 2
  s.cycle()
  assert s.outd[0] == 0xFF
  assert s.outd[1] == 0xFF
  assert s.outd[2] == 0xFF
  assert s.outd[3] == 3
  assert s.outd[4] == 0xFF
  assert s.outw[0] == 0
  assert s.outw[1] == 1
  assert s.outw[2] == 2
  assert s.outw[3] == 4
  assert s.outw[4] == 4
  for i in range(5):
    s.in_[i] = 2
  s.cycle()
  assert s.outd[0] == 0xFF
  assert s.outd[1] == 0xFF
  assert s.outd[2] == 0xFF
  assert s.outd[3] == 4
  assert s.outd[4] == 0xFF
  assert s.outw[0] == 0
  assert s.outw[1] == 1
  assert s.outw[2] == 2
  assert s.outw[3] == 0
  assert s.outw[4] == 4

#-----------------------------------------------------------------------
# Router
#-----------------------------------------------------------------------
#   00 - 01 - 02 - 03
#   |    |    |    |
#   04 - 05 - 06 - 07
#   |    |    |    |
#   08 - 09 - 10 - 11
#   |    |    |    |
#   12 - 13 - 14 - 15
#   NORTH = 0
#   EAST  = 1
#   SOUTH = 2
#   WEST  = 3
#   TERM  = 4

from perf_tests.cffi_net_CL import MeshRouterCL
def test_Router():
  R = MeshRouterCL
  s = translate( R( 5, 16, 0,0,0) )
  s.reset()
  X = 'x'
  for i in range(5):
    s.out_rdy[i] = 1
    s.in__val[i] = 0

  def debug():
    print "{:3}:".format(s.ncycles),
    for i in range(5):
      print s.out_msg[i] if s.out_val[i] == 1 else 'x',
    print

  def put(exp):
    for i, j in enumerate( exp ):
      if j == 'x':
        s.in__val[i] = 0
      else:
        s.in__val[i] = 1
        s.in__msg[i] = j

  def check(exp):
    for i, j in enumerate( exp ):
      print 'checking', i,j
      if j == 'x':
        assert s.out_val[i] == 0
      else:
        assert s.out_val[i] == 1
        assert s.out_msg[i] == j

  put([ 1, 6, 9, 4, 5])
  s.cycle(); debug(); check([ X, X, X, X, X])
  put([ X, X, X, X, X])
  s.cycle(); debug(); check([ 1, 6, 9, 4, 5])
  s.cycle(); debug(); check([ X, X, X, X, X])
  s.cycle(); debug(); check([ X, X, X, X, X])
  put([ 6, 9, 4, 5, 1])
  s.cycle(); debug(); check([ X, X, X, X, X])
  put([ 4, 5, 1, 6, 9])
  s.cycle(); debug(); check([ 1, 6, 9, 4, 5])
  put([ X, X, X, X, X])
  s.cycle(); debug(); check([ 1, 6, 9, 4, 5])
  put([ 9, 9, 9, 9, 9])
  s.cycle(); debug(); check([ X, X, X, X, X])
  put([ X, X, X, X, X])
  s.cycle(); debug(); check([ X, X, 9, X, X])
  s.cycle(); debug(); check([ X, X, 9, X, X])
  s.cycle(); debug(); check([ X, X, 9, X, X])
  s.cycle(); debug(); check([ X, X, 9, X, X])
  s.cycle(); debug(); check([ X, X, 9, X, X])
  s.cycle(); debug(); check([ X, X, X, X, X])


#-----------------------------------------------------------------------
# ValRdyQueues
#-----------------------------------------------------------------------
#from pclib.queues import InValRdyQueue, OutValRdyQueue
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
