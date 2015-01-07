#=========================================================================
# ParcProcFL_test
#=========================================================================

from __future__ import print_function

import pytest
import pisa
import struct

from pymtl        import *
from pclib.test   import TestSource, TestSink, TestMemory
from pclib.ifcs import mem_msgs
from ParcProcCL   import ParcProcCL

from accel.mvmult.mvmult_fl  import MatrixVecFL
from accel.mvmult.mvmult_cl  import MatrixVecCL

from pisa.pisa_inst_test_utils import asm_test

class TestHarness (Model):

  #-----------------------------------------------------------------------
  # constructor
  #-----------------------------------------------------------------------

  def __init__( s, XcelModel, mem_delay ):

    # Create parameters

    memreq_p  = mem_msgs.MemReqParams(32,32)
    memresp_p = mem_msgs.MemRespParams(32)

    # Instantiate models

    s.src    = TestSource  ( 32, [], 0 )
    s.sink   = TestSink    ( 32, [], 0 )
    s.proc   = ParcProcCL  ()
    s.mem    = TestMemory  ( memreq_p, memresp_p, 3, mem_delay )
    s.mvmult = XcelModel   ()

  #-----------------------------------------------------------------------
  # elaborate
  #-----------------------------------------------------------------------

  def elaborate_logic( s ):

    # Processor <-> Proc/Mngr

    s.connect( s.proc.mngr2proc, s.src.out         )
    s.connect( s.proc.proc2mngr, s.sink.in_        )
    s.connect( s.proc.go,        1                 )

    # Processor <-> Memory

    s.connect( s.proc.imemreq,   s.mem.reqs[0]     )
    s.connect( s.proc.imemresp,  s.mem.resps[0]    )
    s.connect( s.proc.dmemreq,   s.mem.reqs[1]     )
    s.connect( s.proc.dmemresp,  s.mem.resps[1]    )

    # Processor <-> Accelerator

    s.connect( s.proc.to_cp2,    s.mvmult.from_cpu )
    s.connect( s.proc.from_cp2,  s.mvmult.to_cpu   )

    # Accelerator <-> Memory

    s.connect( s.mvmult.memreq,  s.mem.reqs[2]     )
    s.connect( s.mvmult.memresp, s.mem.resps[2]    )

  #-----------------------------------------------------------------------
  # load
  #-----------------------------------------------------------------------

  def load( self, mem_image ):

    # Iterate over the sections

    sections = mem_image.get_sections()
    for section in sections:

      # For .mngr2proc sections, copy section into mngr2proc src

      if section.name == ".mngr2proc":
        for i in xrange(0,len(section.data),4):
          bits = struct.unpack_from("<I",buffer(section.data,i,4))[0]
          self.src.src.msgs.append( Bits(32,bits) )

      # For .proc2mngr sections, copy section into proc2mngr_ref src

      elif section.name == ".proc2mngr":
        for i in xrange(0,len(section.data),4):
          bits = struct.unpack_from("<I",buffer(section.data,i,4))[0]
          self.sink.sink.msgs.append( Bits(32,bits) )

      # For all other sections, simply copy them into the memory

      else:
        start_addr = section.addr
        stop_addr  = section.addr + len(section.data)
        self.mem.mem.mem[start_addr:stop_addr] = section.data

  #-----------------------------------------------------------------------
  # cleanup
  #-----------------------------------------------------------------------

  def cleanup( s ):
    del s.mem.mem.mem[:]

  #-----------------------------------------------------------------------
  # done
  #-----------------------------------------------------------------------

  def done( s ):
    return s.src.done and s.sink.done

  #-----------------------------------------------------------------------
  # line_trace
  #-----------------------------------------------------------------------

  def line_trace( s ):
    return s.src.line_trace()    + " > " + \
           s.proc.line_trace()   + " " + \
           s.mvmult.line_trace() + " " + \
           s.mem.line_trace()    + " > " + \
           s.sink.line_trace()

#-------------------------------------------------------------------------
# run_test
#-------------------------------------------------------------------------

def run_test( gen_test, XcelModel=MatrixVecFL ):

  # Instantiate and elaborate the model

  model = TestHarness( XcelModel, 0 )
  model.elaborate()

  # Assemble the test program

  mem_image = pisa.pisa_encoding.assemble( gen_test() )

  # Load the program into the model

  model.load( mem_image )

  # Create a simulator using the simulation tool

  sim = SimulationTool( model )

  # Run the simulation

  print()

  sim.reset()
  while not model.done():
    sim.print_line_trace()
    sim.cycle()

  # Add a couple extra ticks so that the VCD dump is nicer

  sim.cycle()
  sim.cycle()
  sim.cycle()

  model.cleanup()

#-------------------------------------------------------------------------
# mngr
#-------------------------------------------------------------------------

import pisa.pisa_inst_mngr_test

@pytest.mark.parametrize( "name,test", [
  asm_test( pisa.pisa_inst_mngr_test.gen_basic_test  ),
  asm_test( pisa.pisa_inst_mngr_test.gen_bypass_test ),
  asm_test( pisa.pisa_inst_mngr_test.gen_value_test  ),
])
def test_mngr( name, test ):
  run_test( test )

#-------------------------------------------------------------------------
# addu
#-------------------------------------------------------------------------

import pisa.pisa_inst_addu_test

@pytest.mark.parametrize( "name,test", [
  asm_test( pisa.pisa_inst_addu_test.gen_basic_test     ),
  asm_test( pisa.pisa_inst_addu_test.gen_dest_byp_test  ),
  asm_test( pisa.pisa_inst_addu_test.gen_src0_byp_test  ),
  asm_test( pisa.pisa_inst_addu_test.gen_src1_byp_test  ),
  asm_test( pisa.pisa_inst_addu_test.gen_srcs_byp_test  ),
  asm_test( pisa.pisa_inst_addu_test.gen_srcs_dest_test ),
  asm_test( pisa.pisa_inst_addu_test.gen_value_test     ),
  asm_test( pisa.pisa_inst_addu_test.gen_random_test    ),
])
def test_addu( name, test ):
  run_test( test )

#-------------------------------------------------------------------------
# subu
#-------------------------------------------------------------------------

import pisa.pisa_inst_subu_test

@pytest.mark.parametrize( "name,test", [
  asm_test( pisa.pisa_inst_subu_test.gen_basic_test     ),
  asm_test( pisa.pisa_inst_subu_test.gen_dest_byp_test  ),
  asm_test( pisa.pisa_inst_subu_test.gen_src0_byp_test  ),
  asm_test( pisa.pisa_inst_subu_test.gen_src1_byp_test  ),
  asm_test( pisa.pisa_inst_subu_test.gen_srcs_byp_test  ),
  asm_test( pisa.pisa_inst_subu_test.gen_srcs_dest_test ),
  asm_test( pisa.pisa_inst_subu_test.gen_value_test     ),
  asm_test( pisa.pisa_inst_subu_test.gen_random_test    ),
])
def test_subu( name, test ):
  run_test( test )

#-------------------------------------------------------------------------
# and
#-------------------------------------------------------------------------

import pisa.pisa_inst_and_test

@pytest.mark.parametrize( "name,test", [
  asm_test( pisa.pisa_inst_and_test.gen_basic_test     ),
  asm_test( pisa.pisa_inst_and_test.gen_dest_byp_test  ),
  asm_test( pisa.pisa_inst_and_test.gen_src0_byp_test  ),
  asm_test( pisa.pisa_inst_and_test.gen_src1_byp_test  ),
  asm_test( pisa.pisa_inst_and_test.gen_srcs_byp_test  ),
  asm_test( pisa.pisa_inst_and_test.gen_srcs_dest_test ),
  asm_test( pisa.pisa_inst_and_test.gen_value_test     ),
  asm_test( pisa.pisa_inst_and_test.gen_random_test    ),
])
def test_and( name, test ):
  run_test( test )

#-------------------------------------------------------------------------
# or
#-------------------------------------------------------------------------

import pisa.pisa_inst_or_test

@pytest.mark.parametrize( "name,test", [
  asm_test( pisa.pisa_inst_or_test.gen_basic_test     ),
  asm_test( pisa.pisa_inst_or_test.gen_dest_byp_test  ),
  asm_test( pisa.pisa_inst_or_test.gen_src0_byp_test  ),
  asm_test( pisa.pisa_inst_or_test.gen_src1_byp_test  ),
  asm_test( pisa.pisa_inst_or_test.gen_srcs_byp_test  ),
  asm_test( pisa.pisa_inst_or_test.gen_srcs_dest_test ),
  asm_test( pisa.pisa_inst_or_test.gen_value_test     ),
  asm_test( pisa.pisa_inst_or_test.gen_random_test    ),
])
def test_or( name, test ):
  run_test( test )

#-------------------------------------------------------------------------
# xor
#-------------------------------------------------------------------------

import pisa.pisa_inst_xor_test

@pytest.mark.parametrize( "name,test", [
  asm_test( pisa.pisa_inst_xor_test.gen_basic_test     ),
  asm_test( pisa.pisa_inst_xor_test.gen_dest_byp_test  ),
  asm_test( pisa.pisa_inst_xor_test.gen_src0_byp_test  ),
  asm_test( pisa.pisa_inst_xor_test.gen_src1_byp_test  ),
  asm_test( pisa.pisa_inst_xor_test.gen_srcs_byp_test  ),
  asm_test( pisa.pisa_inst_xor_test.gen_srcs_dest_test ),
  asm_test( pisa.pisa_inst_xor_test.gen_value_test     ),
  asm_test( pisa.pisa_inst_xor_test.gen_random_test    ),
])
def test_xor( name, test ):
  run_test( test )

#-------------------------------------------------------------------------
# nor
#-------------------------------------------------------------------------

import pisa.pisa_inst_nor_test

@pytest.mark.parametrize( "name,test", [
  asm_test( pisa.pisa_inst_nor_test.gen_basic_test     ),
  asm_test( pisa.pisa_inst_nor_test.gen_dest_byp_test  ),
  asm_test( pisa.pisa_inst_nor_test.gen_src0_byp_test  ),
  asm_test( pisa.pisa_inst_nor_test.gen_src1_byp_test  ),
  asm_test( pisa.pisa_inst_nor_test.gen_srcs_byp_test  ),
  asm_test( pisa.pisa_inst_nor_test.gen_srcs_dest_test ),
  asm_test( pisa.pisa_inst_nor_test.gen_value_test     ),
  asm_test( pisa.pisa_inst_nor_test.gen_random_test    ),
])
def test_nor( name, test ):
  run_test( test )

#-------------------------------------------------------------------------
# slt
#-------------------------------------------------------------------------

import pisa.pisa_inst_slt_test

@pytest.mark.parametrize( "name,test", [
  asm_test( pisa.pisa_inst_slt_test.gen_basic_test     ),
  asm_test( pisa.pisa_inst_slt_test.gen_dest_byp_test  ),
  asm_test( pisa.pisa_inst_slt_test.gen_src0_byp_test  ),
  asm_test( pisa.pisa_inst_slt_test.gen_src1_byp_test  ),
  asm_test( pisa.pisa_inst_slt_test.gen_srcs_byp_test  ),
  asm_test( pisa.pisa_inst_slt_test.gen_srcs_dest_test ),
  asm_test( pisa.pisa_inst_slt_test.gen_value_test     ),
  asm_test( pisa.pisa_inst_slt_test.gen_random_test    ),
])
def test_slt( name, test ):
  run_test( test )

#-------------------------------------------------------------------------
# sltu
#-------------------------------------------------------------------------

import pisa.pisa_inst_sltu_test

@pytest.mark.parametrize( "name,test", [
  asm_test( pisa.pisa_inst_sltu_test.gen_basic_test     ),
  asm_test( pisa.pisa_inst_sltu_test.gen_dest_byp_test  ),
  asm_test( pisa.pisa_inst_sltu_test.gen_src0_byp_test  ),
  asm_test( pisa.pisa_inst_sltu_test.gen_src1_byp_test  ),
  asm_test( pisa.pisa_inst_sltu_test.gen_srcs_byp_test  ),
  asm_test( pisa.pisa_inst_sltu_test.gen_srcs_dest_test ),
  asm_test( pisa.pisa_inst_sltu_test.gen_value_test     ),
  asm_test( pisa.pisa_inst_sltu_test.gen_random_test    ),
])
def test_sltu( name, test ):
  run_test( test )

#-------------------------------------------------------------------------
# addiu
#-------------------------------------------------------------------------

import pisa.pisa_inst_addiu_test

@pytest.mark.parametrize( "name,test", [
  asm_test( pisa.pisa_inst_addiu_test.gen_basic_test     ),
  asm_test( pisa.pisa_inst_addiu_test.gen_dest_byp_test  ),
  asm_test( pisa.pisa_inst_addiu_test.gen_src_byp_test   ),
  asm_test( pisa.pisa_inst_addiu_test.gen_srcs_dest_test ),
  asm_test( pisa.pisa_inst_addiu_test.gen_value_test     ),
  asm_test( pisa.pisa_inst_addiu_test.gen_random_test    ),
])
def test_addiu( name, test ):
  run_test( test )

#-------------------------------------------------------------------------
# andi
#-------------------------------------------------------------------------

import pisa.pisa_inst_andi_test

@pytest.mark.parametrize( "name,test", [
  asm_test( pisa.pisa_inst_andi_test.gen_basic_test     ),
  asm_test( pisa.pisa_inst_andi_test.gen_dest_byp_test  ),
  asm_test( pisa.pisa_inst_andi_test.gen_src_byp_test   ),
  asm_test( pisa.pisa_inst_andi_test.gen_srcs_dest_test ),
  asm_test( pisa.pisa_inst_andi_test.gen_value_test     ),
  asm_test( pisa.pisa_inst_andi_test.gen_random_test    ),
])
def test_andi( name, test ):
  run_test( test )

#-------------------------------------------------------------------------
# ori
#-------------------------------------------------------------------------

import pisa.pisa_inst_ori_test

@pytest.mark.parametrize( "name,test", [
  asm_test( pisa.pisa_inst_ori_test.gen_basic_test     ),
  asm_test( pisa.pisa_inst_ori_test.gen_dest_byp_test  ),
  asm_test( pisa.pisa_inst_ori_test.gen_src_byp_test   ),
  asm_test( pisa.pisa_inst_ori_test.gen_srcs_dest_test ),
  asm_test( pisa.pisa_inst_ori_test.gen_value_test     ),
  asm_test( pisa.pisa_inst_ori_test.gen_random_test    ),
])
def test_ori( name, test ):
  run_test( test )

#-------------------------------------------------------------------------
# xori
#-------------------------------------------------------------------------

import pisa.pisa_inst_xori_test

@pytest.mark.parametrize( "name,test", [
  asm_test( pisa.pisa_inst_xori_test.gen_basic_test     ),
  asm_test( pisa.pisa_inst_xori_test.gen_dest_byp_test  ),
  asm_test( pisa.pisa_inst_xori_test.gen_src_byp_test   ),
  asm_test( pisa.pisa_inst_xori_test.gen_srcs_dest_test ),
  asm_test( pisa.pisa_inst_xori_test.gen_value_test     ),
  asm_test( pisa.pisa_inst_xori_test.gen_random_test    ),
])
def test_xori( name, test ):
  run_test( test )

#-------------------------------------------------------------------------
# slti
#-------------------------------------------------------------------------

import pisa.pisa_inst_slti_test

@pytest.mark.parametrize( "name,test", [
  asm_test( pisa.pisa_inst_slti_test.gen_basic_test     ),
  asm_test( pisa.pisa_inst_slti_test.gen_dest_byp_test  ),
  asm_test( pisa.pisa_inst_slti_test.gen_src_byp_test   ),
  asm_test( pisa.pisa_inst_slti_test.gen_srcs_dest_test ),
  asm_test( pisa.pisa_inst_slti_test.gen_value_test     ),
  asm_test( pisa.pisa_inst_slti_test.gen_random_test    ),
])
def test_slti( name, test ):
  run_test( test )

#-------------------------------------------------------------------------
# sltiu
#-------------------------------------------------------------------------

import pisa.pisa_inst_sltiu_test

@pytest.mark.parametrize( "name,test", [
  asm_test( pisa.pisa_inst_sltiu_test.gen_basic_test     ),
  asm_test( pisa.pisa_inst_sltiu_test.gen_dest_byp_test  ),
  asm_test( pisa.pisa_inst_sltiu_test.gen_src_byp_test   ),
  asm_test( pisa.pisa_inst_sltiu_test.gen_srcs_dest_test ),
  asm_test( pisa.pisa_inst_sltiu_test.gen_value_test     ),
  asm_test( pisa.pisa_inst_sltiu_test.gen_random_test    ),
])
def test_sltiu( name, test ):
  run_test( test )

#-------------------------------------------------------------------------
# sll
#-------------------------------------------------------------------------

import pisa.pisa_inst_sll_test

@pytest.mark.parametrize( "name,test", [
  asm_test( pisa.pisa_inst_sll_test.gen_basic_test     ),
  asm_test( pisa.pisa_inst_sll_test.gen_dest_byp_test  ),
  asm_test( pisa.pisa_inst_sll_test.gen_src_byp_test   ),
  asm_test( pisa.pisa_inst_sll_test.gen_srcs_dest_test ),
  asm_test( pisa.pisa_inst_sll_test.gen_value_test     ),
  asm_test( pisa.pisa_inst_sll_test.gen_random_test    ),
])
def test_sll( name, test ):
  run_test( test )

#-------------------------------------------------------------------------
# srl
#-------------------------------------------------------------------------

import pisa.pisa_inst_srl_test

@pytest.mark.parametrize( "name,test", [
  asm_test( pisa.pisa_inst_srl_test.gen_basic_test     ),
  asm_test( pisa.pisa_inst_srl_test.gen_dest_byp_test  ),
  asm_test( pisa.pisa_inst_srl_test.gen_src_byp_test   ),
  asm_test( pisa.pisa_inst_srl_test.gen_srcs_dest_test ),
  asm_test( pisa.pisa_inst_srl_test.gen_value_test     ),
  asm_test( pisa.pisa_inst_srl_test.gen_random_test    ),
])
def test_srl( name, test ):
  run_test( test )

#-------------------------------------------------------------------------
# sra
#-------------------------------------------------------------------------

import pisa.pisa_inst_sra_test

@pytest.mark.parametrize( "name,test", [
  asm_test( pisa.pisa_inst_sra_test.gen_basic_test     ),
  asm_test( pisa.pisa_inst_sra_test.gen_dest_byp_test  ),
  asm_test( pisa.pisa_inst_sra_test.gen_src_byp_test   ),
  asm_test( pisa.pisa_inst_sra_test.gen_srcs_dest_test ),
  asm_test( pisa.pisa_inst_sra_test.gen_value_test     ),
  asm_test( pisa.pisa_inst_sra_test.gen_random_test    ),
])
def test_sra( name, test ):
  run_test( test )

#-------------------------------------------------------------------------
# sllv
#-------------------------------------------------------------------------

import pisa.pisa_inst_sllv_test

@pytest.mark.parametrize( "name,test", [
  asm_test( pisa.pisa_inst_sllv_test.gen_basic_test     ),
  asm_test( pisa.pisa_inst_sllv_test.gen_dest_byp_test  ),
  asm_test( pisa.pisa_inst_sllv_test.gen_src0_byp_test  ),
  asm_test( pisa.pisa_inst_sllv_test.gen_src1_byp_test  ),
  asm_test( pisa.pisa_inst_sllv_test.gen_srcs_byp_test  ),
  asm_test( pisa.pisa_inst_sllv_test.gen_srcs_dest_test ),
  asm_test( pisa.pisa_inst_sllv_test.gen_value_test     ),
  asm_test( pisa.pisa_inst_sllv_test.gen_random_test    ),
])
def test_sllv( name, test ):
  run_test( test )

#-------------------------------------------------------------------------
# srlv
#-------------------------------------------------------------------------

import pisa.pisa_inst_srlv_test

@pytest.mark.parametrize( "name,test", [
  asm_test( pisa.pisa_inst_srlv_test.gen_basic_test     ),
  asm_test( pisa.pisa_inst_srlv_test.gen_dest_byp_test  ),
  asm_test( pisa.pisa_inst_srlv_test.gen_src0_byp_test  ),
  asm_test( pisa.pisa_inst_srlv_test.gen_src1_byp_test  ),
  asm_test( pisa.pisa_inst_srlv_test.gen_srcs_byp_test  ),
  asm_test( pisa.pisa_inst_srlv_test.gen_srcs_dest_test ),
  asm_test( pisa.pisa_inst_srlv_test.gen_value_test     ),
  asm_test( pisa.pisa_inst_srlv_test.gen_random_test    ),
])
def test_srlv( name, test ):
  run_test( test )

#-------------------------------------------------------------------------
# srav
#-------------------------------------------------------------------------

import pisa.pisa_inst_srav_test

@pytest.mark.parametrize( "name,test", [
  asm_test( pisa.pisa_inst_srav_test.gen_basic_test     ),
  asm_test( pisa.pisa_inst_srav_test.gen_dest_byp_test  ),
  asm_test( pisa.pisa_inst_srav_test.gen_src0_byp_test  ),
  asm_test( pisa.pisa_inst_srav_test.gen_src1_byp_test  ),
  asm_test( pisa.pisa_inst_srav_test.gen_srcs_byp_test  ),
  asm_test( pisa.pisa_inst_srav_test.gen_srcs_dest_test ),
  asm_test( pisa.pisa_inst_srav_test.gen_value_test     ),
  asm_test( pisa.pisa_inst_srav_test.gen_random_test    ),
])
def test_srav( name, test ):
  run_test( test )

#-------------------------------------------------------------------------
# lui
#-------------------------------------------------------------------------

import pisa.pisa_inst_lui_test

@pytest.mark.parametrize( "name,test", [
  asm_test( pisa.pisa_inst_lui_test.gen_basic_test     ),
  asm_test( pisa.pisa_inst_lui_test.gen_dest_byp_test  ),
  asm_test( pisa.pisa_inst_lui_test.gen_value_test     ),
  asm_test( pisa.pisa_inst_lui_test.gen_random_test    ),
])
def test_lui( name, test ):
  run_test( test )

#-------------------------------------------------------------------------
# mul
#-------------------------------------------------------------------------

import pisa.pisa_inst_mul_test

@pytest.mark.parametrize( "name,test", [
  asm_test( pisa.pisa_inst_mul_test.gen_basic_test     ),
  asm_test( pisa.pisa_inst_mul_test.gen_dest_byp_test  ),
  asm_test( pisa.pisa_inst_mul_test.gen_src0_byp_test  ),
  asm_test( pisa.pisa_inst_mul_test.gen_src1_byp_test  ),
  asm_test( pisa.pisa_inst_mul_test.gen_srcs_byp_test  ),
  asm_test( pisa.pisa_inst_mul_test.gen_srcs_dest_test ),
  asm_test( pisa.pisa_inst_mul_test.gen_value_test     ),
  asm_test( pisa.pisa_inst_mul_test.gen_random_test    ),
])
def test_mul( name, test ):
  run_test( test )

#-------------------------------------------------------------------------
# div
#-------------------------------------------------------------------------

import pisa.pisa_inst_div_test

@pytest.mark.parametrize( "name,test", [
  asm_test( pisa.pisa_inst_div_test.gen_basic_test     ),
  asm_test( pisa.pisa_inst_div_test.gen_dest_byp_test  ),
  asm_test( pisa.pisa_inst_div_test.gen_src0_byp_test  ),
  asm_test( pisa.pisa_inst_div_test.gen_src1_byp_test  ),
  asm_test( pisa.pisa_inst_div_test.gen_srcs_byp_test  ),
  asm_test( pisa.pisa_inst_div_test.gen_srcs_dest_test ),
  asm_test( pisa.pisa_inst_div_test.gen_value_test     ),
  asm_test( pisa.pisa_inst_div_test.gen_random_test    ),
])
def test_div( name, test ):
  run_test( test )

#-------------------------------------------------------------------------
# divu
#-------------------------------------------------------------------------

import pisa.pisa_inst_divu_test

@pytest.mark.parametrize( "name,test", [
  asm_test( pisa.pisa_inst_divu_test.gen_basic_test     ),
  asm_test( pisa.pisa_inst_divu_test.gen_dest_byp_test  ),
  asm_test( pisa.pisa_inst_divu_test.gen_src0_byp_test  ),
  asm_test( pisa.pisa_inst_divu_test.gen_src1_byp_test  ),
  asm_test( pisa.pisa_inst_divu_test.gen_srcs_byp_test  ),
  asm_test( pisa.pisa_inst_divu_test.gen_srcs_dest_test ),
  asm_test( pisa.pisa_inst_divu_test.gen_value_test     ),
  asm_test( pisa.pisa_inst_divu_test.gen_random_test    ),
])
def test_divu( name, test ):
  run_test( test )

#-------------------------------------------------------------------------
# rem
#-------------------------------------------------------------------------

import pisa.pisa_inst_rem_test

@pytest.mark.parametrize( "name,test", [
  asm_test( pisa.pisa_inst_rem_test.gen_basic_test     ),
  asm_test( pisa.pisa_inst_rem_test.gen_dest_byp_test  ),
  asm_test( pisa.pisa_inst_rem_test.gen_src0_byp_test  ),
  asm_test( pisa.pisa_inst_rem_test.gen_src1_byp_test  ),
  asm_test( pisa.pisa_inst_rem_test.gen_srcs_byp_test  ),
  asm_test( pisa.pisa_inst_rem_test.gen_srcs_dest_test ),
  asm_test( pisa.pisa_inst_rem_test.gen_value_test     ),
  asm_test( pisa.pisa_inst_rem_test.gen_random_test    ),
])
def test_rem( name, test ):
  run_test( test )

#-------------------------------------------------------------------------
# remu
#-------------------------------------------------------------------------

import pisa.pisa_inst_remu_test

@pytest.mark.parametrize( "name,test", [
  asm_test( pisa.pisa_inst_remu_test.gen_basic_test     ),
  asm_test( pisa.pisa_inst_remu_test.gen_dest_byp_test  ),
  asm_test( pisa.pisa_inst_remu_test.gen_src0_byp_test  ),
  asm_test( pisa.pisa_inst_remu_test.gen_src1_byp_test  ),
  asm_test( pisa.pisa_inst_remu_test.gen_srcs_byp_test  ),
  asm_test( pisa.pisa_inst_remu_test.gen_srcs_dest_test ),
  asm_test( pisa.pisa_inst_remu_test.gen_value_test     ),
  asm_test( pisa.pisa_inst_remu_test.gen_random_test    ),
])
def test_remu( name, test ):
  run_test( test )

#-------------------------------------------------------------------------
# lw
#-------------------------------------------------------------------------

import pisa.pisa_inst_lw_test

@pytest.mark.parametrize( "name,test", [
  asm_test( pisa.pisa_inst_lw_test.gen_basic_test     ),
  asm_test( pisa.pisa_inst_lw_test.gen_dest_byp_test  ),
  asm_test( pisa.pisa_inst_lw_test.gen_base_byp_test   ),
  asm_test( pisa.pisa_inst_lw_test.gen_srcs_dest_test ),
  asm_test( pisa.pisa_inst_lw_test.gen_value_test     ),
  asm_test( pisa.pisa_inst_lw_test.gen_random_test    ),
])
def test_lw( name, test ):
  run_test( test )

#-------------------------------------------------------------------------
# lh
#-------------------------------------------------------------------------

import pisa.pisa_inst_lh_test

@pytest.mark.parametrize( "name,test", [
  asm_test( pisa.pisa_inst_lh_test.gen_basic_test     ),
  asm_test( pisa.pisa_inst_lh_test.gen_dest_byp_test  ),
  asm_test( pisa.pisa_inst_lh_test.gen_base_byp_test   ),
  asm_test( pisa.pisa_inst_lh_test.gen_srcs_dest_test ),
  asm_test( pisa.pisa_inst_lh_test.gen_value_test     ),
  asm_test( pisa.pisa_inst_lh_test.gen_random_test    ),
])
def test_lh( name, test ):
  run_test( test )

#-------------------------------------------------------------------------
# lhu
#-------------------------------------------------------------------------

import pisa.pisa_inst_lhu_test

@pytest.mark.parametrize( "name,test", [
  asm_test( pisa.pisa_inst_lhu_test.gen_basic_test     ),
  asm_test( pisa.pisa_inst_lhu_test.gen_dest_byp_test  ),
  asm_test( pisa.pisa_inst_lhu_test.gen_base_byp_test   ),
  asm_test( pisa.pisa_inst_lhu_test.gen_srcs_dest_test ),
  asm_test( pisa.pisa_inst_lhu_test.gen_value_test     ),
  asm_test( pisa.pisa_inst_lhu_test.gen_random_test    ),
])
def test_lhu( name, test ):
  run_test( test )

#-------------------------------------------------------------------------
# lb
#-------------------------------------------------------------------------

import pisa.pisa_inst_lb_test

@pytest.mark.parametrize( "name,test", [
  asm_test( pisa.pisa_inst_lb_test.gen_basic_test     ),
  asm_test( pisa.pisa_inst_lb_test.gen_dest_byp_test  ),
  asm_test( pisa.pisa_inst_lb_test.gen_base_byp_test   ),
  asm_test( pisa.pisa_inst_lb_test.gen_srcs_dest_test ),
  asm_test( pisa.pisa_inst_lb_test.gen_value_test     ),
  asm_test( pisa.pisa_inst_lb_test.gen_random_test    ),
])
def test_lb( name, test ):
  run_test( test )

#-------------------------------------------------------------------------
# lbu
#-------------------------------------------------------------------------

import pisa.pisa_inst_lbu_test

@pytest.mark.parametrize( "name,test", [
  asm_test( pisa.pisa_inst_lbu_test.gen_basic_test     ),
  asm_test( pisa.pisa_inst_lbu_test.gen_dest_byp_test  ),
  asm_test( pisa.pisa_inst_lbu_test.gen_base_byp_test   ),
  asm_test( pisa.pisa_inst_lbu_test.gen_srcs_dest_test ),
  asm_test( pisa.pisa_inst_lbu_test.gen_value_test     ),
  asm_test( pisa.pisa_inst_lbu_test.gen_random_test    ),
])
def test_lbu( name, test ):
  run_test( test )

#-------------------------------------------------------------------------
# sw
#-------------------------------------------------------------------------

import pisa.pisa_inst_sw_test

@pytest.mark.parametrize( "name,test", [
  asm_test( pisa.pisa_inst_sw_test.gen_basic_test     ),
  asm_test( pisa.pisa_inst_sw_test.gen_dest_byp_test  ),
  asm_test( pisa.pisa_inst_sw_test.gen_base_byp_test  ),
  asm_test( pisa.pisa_inst_sw_test.gen_src_byp_test   ),
  asm_test( pisa.pisa_inst_sw_test.gen_srcs_byp_test  ),
  asm_test( pisa.pisa_inst_sw_test.gen_srcs_dest_test ),
  asm_test( pisa.pisa_inst_sw_test.gen_value_test     ),
  asm_test( pisa.pisa_inst_sw_test.gen_random_test    ),
])
def test_sw( name, test ):
  run_test( test )

#-------------------------------------------------------------------------
# sh
#-------------------------------------------------------------------------

import pisa.pisa_inst_sh_test

@pytest.mark.parametrize( "name,test", [
  asm_test( pisa.pisa_inst_sh_test.gen_basic_test     ),
  asm_test( pisa.pisa_inst_sh_test.gen_dest_byp_test  ),
  asm_test( pisa.pisa_inst_sh_test.gen_base_byp_test  ),
  asm_test( pisa.pisa_inst_sh_test.gen_src_byp_test   ),
  asm_test( pisa.pisa_inst_sh_test.gen_srcs_byp_test  ),
  asm_test( pisa.pisa_inst_sh_test.gen_srcs_dest_test ),
  asm_test( pisa.pisa_inst_sh_test.gen_value_test     ),
  asm_test( pisa.pisa_inst_sh_test.gen_random_test    ),
])
def test_sh( name, test ):
  run_test( test )

#-------------------------------------------------------------------------
# sb
#-------------------------------------------------------------------------

import pisa.pisa_inst_sb_test

@pytest.mark.parametrize( "name,test", [
  asm_test( pisa.pisa_inst_sb_test.gen_basic_test     ),
  asm_test( pisa.pisa_inst_sb_test.gen_dest_byp_test  ),
  asm_test( pisa.pisa_inst_sb_test.gen_base_byp_test  ),
  asm_test( pisa.pisa_inst_sb_test.gen_src_byp_test   ),
  asm_test( pisa.pisa_inst_sb_test.gen_srcs_byp_test  ),
  asm_test( pisa.pisa_inst_sb_test.gen_srcs_dest_test ),
  asm_test( pisa.pisa_inst_sb_test.gen_value_test     ),
  asm_test( pisa.pisa_inst_sb_test.gen_random_test    ),
])
def test_sb( name, test ):
  run_test( test )

#-------------------------------------------------------------------------
# j
#-------------------------------------------------------------------------

import pisa.pisa_inst_j_test

@pytest.mark.parametrize( "name,test", [
  asm_test( pisa.pisa_inst_j_test.gen_basic_test ),
  asm_test( pisa.pisa_inst_j_test.gen_jump_test  ),
])
def test_j( name, test ):
  run_test( test )

#-------------------------------------------------------------------------
# jal
#-------------------------------------------------------------------------

import pisa.pisa_inst_jal_test

@pytest.mark.parametrize( "name,test", [
  asm_test( pisa.pisa_inst_jal_test.gen_basic_test    ),
  asm_test( pisa.pisa_inst_jal_test.gen_link_byp_test ),
  asm_test( pisa.pisa_inst_jal_test.gen_jump_test     ),
])
def test_jal( name, test ):
  run_test( test )

#-------------------------------------------------------------------------
# jr
#-------------------------------------------------------------------------

import pisa.pisa_inst_jr_test

@pytest.mark.parametrize( "name,test", [
  asm_test( pisa.pisa_inst_jr_test.gen_basic_test   ),
  asm_test( pisa.pisa_inst_jr_test.gen_src_byp_test ),
  asm_test( pisa.pisa_inst_jr_test.gen_jump_test    ),
])
def test_jr( name, test ):
  run_test( test )

#-------------------------------------------------------------------------
# jalr
#-------------------------------------------------------------------------

import pisa.pisa_inst_jalr_test

@pytest.mark.parametrize( "name,test", [
  asm_test( pisa.pisa_inst_jalr_test.gen_basic_test    ),
  asm_test( pisa.pisa_inst_jalr_test.gen_link_byp_test ),
  asm_test( pisa.pisa_inst_jalr_test.gen_src_byp_test  ),
  asm_test( pisa.pisa_inst_jalr_test.gen_jump_test     ),
])
def test_jalr( name, test ):
  run_test( test )

#-------------------------------------------------------------------------
# beq
#-------------------------------------------------------------------------

import pisa.pisa_inst_beq_test

@pytest.mark.parametrize( "name,test", [
  asm_test( pisa.pisa_inst_beq_test.gen_basic_test             ),
  asm_test( pisa.pisa_inst_beq_test.gen_src0_byp_taken_test    ),
  asm_test( pisa.pisa_inst_beq_test.gen_src0_byp_nottaken_test ),
  asm_test( pisa.pisa_inst_beq_test.gen_src1_byp_taken_test    ),
  asm_test( pisa.pisa_inst_beq_test.gen_src1_byp_nottaken_test ),
  asm_test( pisa.pisa_inst_beq_test.gen_srcs_byp_taken_test    ),
  asm_test( pisa.pisa_inst_beq_test.gen_srcs_byp_nottaken_test ),
  asm_test( pisa.pisa_inst_beq_test.gen_src0_eq_src1_test      ),
  asm_test( pisa.pisa_inst_beq_test.gen_value_test             ),
  asm_test( pisa.pisa_inst_beq_test.gen_random_test            ),
])
def test_beq( name, test ):
  run_test( test )

#-------------------------------------------------------------------------
# bne
#-------------------------------------------------------------------------

import pisa.pisa_inst_bne_test

@pytest.mark.parametrize( "name,test", [
  asm_test( pisa.pisa_inst_bne_test.gen_basic_test             ),
  asm_test( pisa.pisa_inst_bne_test.gen_src0_byp_taken_test    ),
  asm_test( pisa.pisa_inst_bne_test.gen_src0_byp_nottaken_test ),
  asm_test( pisa.pisa_inst_bne_test.gen_src1_byp_taken_test    ),
  asm_test( pisa.pisa_inst_bne_test.gen_src1_byp_nottaken_test ),
  asm_test( pisa.pisa_inst_bne_test.gen_srcs_byp_taken_test    ),
  asm_test( pisa.pisa_inst_bne_test.gen_srcs_byp_nottaken_test ),
  asm_test( pisa.pisa_inst_bne_test.gen_src0_eq_src1_test      ),
  asm_test( pisa.pisa_inst_bne_test.gen_value_test             ),
  asm_test( pisa.pisa_inst_bne_test.gen_random_test            ),
])
def test_bne( name, test ):
  run_test( test )

#-------------------------------------------------------------------------
# blez
#-------------------------------------------------------------------------

import pisa.pisa_inst_blez_test

@pytest.mark.parametrize( "name,test", [
  asm_test( pisa.pisa_inst_blez_test.gen_basic_test            ),
  asm_test( pisa.pisa_inst_blez_test.gen_src_byp_taken_test    ),
  asm_test( pisa.pisa_inst_blez_test.gen_src_byp_nottaken_test ),
  asm_test( pisa.pisa_inst_blez_test.gen_value_test            ),
  asm_test( pisa.pisa_inst_blez_test.gen_random_test           ),
])
def test_blez( name, test ):
  run_test( test )

#-------------------------------------------------------------------------
# bgtz
#-------------------------------------------------------------------------

import pisa.pisa_inst_bgtz_test

@pytest.mark.parametrize( "name,test", [
  asm_test( pisa.pisa_inst_bgtz_test.gen_basic_test            ),
  asm_test( pisa.pisa_inst_bgtz_test.gen_src_byp_taken_test    ),
  asm_test( pisa.pisa_inst_bgtz_test.gen_src_byp_nottaken_test ),
  asm_test( pisa.pisa_inst_bgtz_test.gen_value_test            ),
  asm_test( pisa.pisa_inst_bgtz_test.gen_random_test           ),
])
def test_bgtz( name, test ):
  run_test( test )

#-------------------------------------------------------------------------
# bltz
#-------------------------------------------------------------------------

import pisa.pisa_inst_bltz_test

@pytest.mark.parametrize( "name,test", [
  asm_test( pisa.pisa_inst_bltz_test.gen_basic_test            ),
  asm_test( pisa.pisa_inst_bltz_test.gen_src_byp_taken_test    ),
  asm_test( pisa.pisa_inst_bltz_test.gen_src_byp_nottaken_test ),
  asm_test( pisa.pisa_inst_bltz_test.gen_value_test            ),
  asm_test( pisa.pisa_inst_bltz_test.gen_random_test           ),
])
def test_bltz( name, test ):
  run_test( test )

#-------------------------------------------------------------------------
# bgez
#-------------------------------------------------------------------------

import pisa.pisa_inst_bgez_test

@pytest.mark.parametrize( "name,test", [
  asm_test( pisa.pisa_inst_bgez_test.gen_basic_test            ),
  asm_test( pisa.pisa_inst_bgez_test.gen_src_byp_taken_test    ),
  asm_test( pisa.pisa_inst_bgez_test.gen_src_byp_nottaken_test ),
  asm_test( pisa.pisa_inst_bgez_test.gen_value_test            ),
  asm_test( pisa.pisa_inst_bgez_test.gen_random_test           ),
])
def test_bgez( name, test ):
  run_test( test )

#-------------------------------------------------------------------------
# mtc2 (with functional-level mvmult impl)
#-------------------------------------------------------------------------

import pisa.pisa_inst_mtc2_test

@pytest.mark.parametrize( "name,test", [
  asm_test( pisa.pisa_inst_mtc2_test.gen_basic_test ),
])
def test_mtc2_fl( name, test ):
  run_test( test )

#-------------------------------------------------------------------------
# mtc2 (with cycle-level mvmult impl)
#-------------------------------------------------------------------------

@pytest.mark.parametrize( "name,test", [
  asm_test( pisa.pisa_inst_mtc2_test.gen_basic_test ),
])
def test_mtc2_cl( name, test ):
  run_test( test, MatrixVecCL )

