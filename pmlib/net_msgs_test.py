#=========================================================================
# net_msgs Test Suite
#=========================================================================

from   pymtl import *
import pmlib
import net_msgs

from   pmlib.TestVectorSimulator import TestVectorSimulator

#-------------------------------------------------------------------------
# test_netmsg_slices
#-------------------------------------------------------------------------

def test_netmsg_slices():

  # Create parameters

  netmsg_params = net_msgs.NetMsgParams( 8, 256, 32 )

  # Create a read request

  msg = Bits( netmsg_params.nbits )
  msg[ netmsg_params.dest_slice    ] = 1
  msg[ netmsg_params.src_slice     ] = 2
  msg[ netmsg_params.seqnum_slice  ] = 255
  msg[ netmsg_params.payload_slice ] = 0xaabbccdd

  assert msg[ netmsg_params.dest_slice    ] == 1
  assert msg[ netmsg_params.src_slice     ] == 2
  assert msg[ netmsg_params.seqnum_slice  ] == 255
  assert msg[ netmsg_params.payload_slice ] == 0xaabbccdd

#-------------------------------------------------------------------------
# test_netmsg_from_bits
#-------------------------------------------------------------------------

def test_memreq_from_bits( dump_vcd ):

  # Create parameters

  netmsg_params = net_msgs.NetMsgParams( 8, 256, 32 )

  # Test vectors

  msg = netmsg_params.mk_msg

  test_vectors = [
    # bits                         dest src seqnum payload
    [ msg( 1, 1, 255, 0xaaaaaaaa ), 1,   1, 255,   0xaaaaaaaa ],
    [ msg( 2, 2, 4,   0xbbbbbbbb ), 2,   2, 4,     0xbbbbbbbb ],
    [ msg( 3, 3, 123, 0xcccccccc ), 3,   3, 123,   0xcccccccc ],
    [ msg( 4, 0, 35,  0xdddddddd ), 4,   0, 35,    0xdddddddd ],
  ]

  # Instantiate and elaborate the model

  model = net_msgs.NetMsgFromBits( netmsg_params )
  model.elaborate()

  # Define functions mapping the test vector to ports in model

  def tv_in( model, test_vector ):
    model.bits.value = test_vector[0]

  def tv_out( model, test_vector ):
    assert model.dest.value    == test_vector[1]
    assert model.src.value     == test_vector[2]
    assert model.seqnum.value  == test_vector[3]
    assert model.payload.value == test_vector[4]

  # Run the test

  sim = TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  if dump_vcd:
    sim.dump_vcd( "net_msgs-test_netmsg_from_bits.vcd" )
  sim.run_test()
