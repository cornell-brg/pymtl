#=========================================================================
# mem_struct Test Suite
#=========================================================================

from pymtl import *
import mem_struct

from TestVectorSimulator import TestVectorSimulator

#-------------------------------------------------------------------------
# test_memreq_from_bits
#-------------------------------------------------------------------------

class MsgTester( Model ):
  def __init__( self, memreq_msg ):
    self.in_ = InPort ( memreq_msg )
    self.out = OutPort( memreq_msg )
    connect( self.in_, self.out )

def test_mkreq( dump_vcd ):

  # Create parameters

  memreq = mem_struct.MemReqMsg( 32, 32 )

  # Test vectors

  req = memreq.mk_req
  r   = memreq.rd
  w   = memreq.wr

  test_vectors = [
    # bits                                 type addr        len data

    [ req( r, 0x00001000, 1, 0x00000000 ), r,   0x00001000, 1,  0x00000000 ],
    [ req( r, 0x00001004, 2, 0x00000000 ), r,   0x00001004, 2,  0x00000000 ],
    [ req( r, 0x00001008, 3, 0x00000000 ), r,   0x00001008, 3,  0x00000000 ],
    [ req( r, 0x0000100c, 0, 0x00000000 ), r,   0x0000100c, 0,  0x00000000 ],

    [ req( w, 0x00001000, 1, 0x000000ab ), w,   0x00001000, 1,  0x000000ab ],
    [ req( w, 0x00001004, 2, 0x0000abcd ), w,   0x00001004, 2,  0x0000abcd ],
    [ req( w, 0x00001008, 3, 0x00abcdef ), w,   0x00001008, 3,  0x00abcdef ],
    [ req( w, 0x0000100c, 0, 0xabcdef01 ), w,   0x0000100c, 0,  0xabcdef01 ],

  ]

  # Instantiate and elaborate the model

  model = MsgTester( memreq )
  model.elaborate()

  # Define functions mapping the test vector to ports in model

  def tv_in( model, test_vector ):
    model.in_.value = test_vector[0]

  def tv_out( model, test_vector ):
    assert model.out.type.value == test_vector[1]
    assert model.out.addr.value == test_vector[2]
    assert model.out.len.value  == test_vector[3]
    assert model.out.data.value == test_vector[4]

  # Run the test

  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  if dump_vcd:
    sim.dump_vcd( "pmlib-mem_struct-test_mkreq.vcd" )
  sim.run_test()

#-------------------------------------------------------------------------
# test_memresp_from_bits
#-------------------------------------------------------------------------

def test_mkresp( dump_vcd ):

  # Create parameters

  memresp = mem_struct.MemRespMsg( 32 )

  # Test vectors

  resp = memresp.mk_resp
  r    = memresp.rd
  w    = memresp.wr

  test_vectors = [
    # bits                      type len data

    [ resp( r, 1, 0x000000ab ), r,   1,  0x000000ab ],
    [ resp( r, 2, 0x0000abcd ), r,   2,  0x0000abcd ],
    [ resp( r, 3, 0x00abcdef ), r,   3,  0x00abcdef ],
    [ resp( r, 0, 0xabcdef01 ), r,   0,  0xabcdef01 ],

    [ resp( w, 0, 0x00000000 ), w,   0,  0x00000000 ],

  ]

  # Instantiate and elaborate the model

  model = MsgTester( memresp )
  model.elaborate()

  # Define functions mapping the test vector to ports in model

  def tv_in( model, test_vector ):
    model.in_.value = test_vector[0]

  def tv_out( model, test_vector ):
    assert model.out.type.value == test_vector[1]
    assert model.out.len.value  == test_vector[2]
    assert model.out.data.value == test_vector[3]

  # Run the test

  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  if dump_vcd:
    sim.dump_vcd( "pmlib-mem_struct-test_mkresp.vcd" )
  sim.run_test()

