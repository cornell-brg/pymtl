#=========================================================================
# mem_msgs_test.py
#=========================================================================

from pymtl import *
from pclib import TestVectorSimulator

import mem_msgs

#-------------------------------------------------------------------------
# test_memreq_slices
#-------------------------------------------------------------------------

def test_memreq_slices():

  # Create parameters

  memreq_params = mem_msgs.MemReqParams( 32, 32 )

  # Create a read request

  msg = Bits( memreq_params.nbits )
  msg[ memreq_params.type_slice ] = memreq_params.type_read
  msg[ memreq_params.addr_slice ] = 0x00001000
  msg[ memreq_params.len_slice  ] = 2
  msg[ memreq_params.data_slice ] = 0x00000000

  assert msg[ memreq_params.type_slice ] == memreq_params.type_read
  assert msg[ memreq_params.addr_slice ] == 0x00001000
  assert msg[ memreq_params.len_slice  ] == 2
  assert msg[ memreq_params.data_slice ] == 0x00000000

  # Create a write request

  msg = Bits( memreq_params.nbits )
  msg[ memreq_params.type_slice ] = memreq_params.type_write
  msg[ memreq_params.addr_slice ] = 0x00000400
  msg[ memreq_params.len_slice  ] = 3
  msg[ memreq_params.data_slice ] = 0x00abcdef

  assert msg[ memreq_params.type_slice ] == memreq_params.type_write
  assert msg[ memreq_params.addr_slice ] == 0x00000400
  assert msg[ memreq_params.len_slice  ] == 3
  assert msg[ memreq_params.data_slice ] == 0x00abcdef

#-------------------------------------------------------------------------
# test_memreq_from_bits
#-------------------------------------------------------------------------

def test_memreq_from_bits( dump_vcd ):

  # Create parameters

  memreq_params = mem_msgs.MemReqParams( 32, 32 )

  # Test vectors

  req = memreq_params.mk_req
  r   = memreq_params.type_read
  w   = memreq_params.type_write

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

  model = mem_msgs.MemReqFromBits( memreq_params )
  model.elaborate()

  # Define functions mapping the test vector to ports in model

  def tv_in( model, test_vector ):
    model.bits.value = test_vector[0]

  def tv_out( model, test_vector ):
    assert model.type_.value == test_vector[1]
    assert model.addr.value  == test_vector[2]
    assert model.len_.value  == test_vector[3]
    assert model.data.value  == test_vector[4]

  # Run the test

  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  if dump_vcd:
    sim.dump_vcd( "pmlib-mem_msgs-test_memreq_from_bits.vcd" )
  sim.run_test()

#-------------------------------------------------------------------------
# test_memresp_slices
#-------------------------------------------------------------------------

def test_memresp_slices():

  # Create parameters

  memresp_params = mem_msgs.MemRespParams( 32 )

  # Create a read response

  msg = Bits( memresp_params.nbits )
  msg[ memresp_params.type_slice ] = memresp_params.type_read
  msg[ memresp_params.len_slice  ] = 2
  msg[ memresp_params.data_slice ] = 0x0000abcd

  assert msg[ memresp_params.type_slice ] == memresp_params.type_read
  assert msg[ memresp_params.len_slice  ] == 2
  assert msg[ memresp_params.data_slice ] == 0x0000abcd

  # Create a write response

  msg = Bits( memresp_params.nbits )
  msg[ memresp_params.type_slice ] = memresp_params.type_write
  msg[ memresp_params.len_slice  ] = 0
  msg[ memresp_params.data_slice ] = 0x00000000

  assert msg[ memresp_params.type_slice ] == memresp_params.type_write
  assert msg[ memresp_params.len_slice  ] == 0
  assert msg[ memresp_params.data_slice ] == 0x00000000

#-------------------------------------------------------------------------
# test_memresp_from_bits
#-------------------------------------------------------------------------

def test_memresp_from_bits( dump_vcd ):

  # Create parameters

  memresp_params = mem_msgs.MemRespParams( 32 )

  # Test vectors

  resp = memresp_params.mk_resp
  r    = memresp_params.type_read
  w    = memresp_params.type_write

  test_vectors = [
    # bits                      type len data

    [ resp( r, 1, 0x000000ab ), r,   1,  0x000000ab ],
    [ resp( r, 2, 0x0000abcd ), r,   2,  0x0000abcd ],
    [ resp( r, 3, 0x00abcdef ), r,   3,  0x00abcdef ],
    [ resp( r, 0, 0xabcdef01 ), r,   0,  0xabcdef01 ],

    [ resp( w, 0, 0x00000000 ), w,   0,  0x00000000 ],

  ]

  # Instantiate and elaborate the model

  model = mem_msgs.MemRespFromBits( memresp_params )
  model.elaborate()

  # Define functions mapping the test vector to ports in model

  def tv_in( model, test_vector ):
    model.bits.value = test_vector[0]

  def tv_out( model, test_vector ):
    assert model.type_.value == test_vector[1]
    assert model.len_.value  == test_vector[2]
    assert model.data.value  == test_vector[3]

  # Run the test

  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  if dump_vcd:
    sim.dump_vcd( "pmlib-mem_msgs-test_memresp_from_bits.vcd" )
  sim.run_test()

