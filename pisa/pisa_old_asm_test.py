#=========================================================================
# pisa_inst_old_asm_test.py
#=========================================================================
# We use py.test to run all of the old-style assembly tests. We assume
# that the assembly tests return 1 on success and return >1 on failure.

import pytest
import subprocess
import os
import elf

from PisaSim import PisaSim

#-------------------------------------------------------------------------
# List of assembly tests
#-------------------------------------------------------------------------
# This should be a list of old-style assembly tests.

asm_tests = \
[

  # Register-register arithmetic, logical, and comparison instructions

  "parcv1/parcv1-addu.S",
  "parcv2/parcv2-subu.S",
  "parcv2/parcv2-and.S",
  "parcv2/parcv2-or.S",
  "parcv2/parcv2-xor.S",
  "parcv2/parcv2-nor.S",
  "parcv2/parcv2-slt.S",
  "parcv2/parcv2-sltu.S",

  # Register-immediate arithmetic, logical, and comparison instructions

  "parcv1/parcv1-addiu.S",
  "parcv2/parcv2-andi.S",
  "parcv1/parcv1-ori.S",
  "parcv2/parcv2-xori.S",
  "parcv2/parcv2-slti.S",
  "parcv2/parcv2-sltiu.S",

  # Shift instructions

  "parcv2/parcv2-sll.S",
  "parcv2/parcv2-srl.S",
  "parcv2/parcv2-sra.S",
  "parcv2/parcv2-sllv.S",
  "parcv2/parcv2-srav.S",
  "parcv2/parcv2-srlv.S",

  # Other instructions

  "parcv1/parcv1-lui.S",

  # Multiply/divide instructions

  "parcv2/parcv2-mul.S",
  "parcv2/parcv2-div.S",
  "parcv2/parcv2-divu.S",
  "parcv2/parcv2-rem.S",
  "parcv2/parcv2-remu.S",

  # Load instructions

  "parcv1/parcv1-lw.S",
  "parcv2/parcv2-lh.S",
  "parcv2/parcv2-lhu.S",
  "parcv2/parcv2-lb.S",
  "parcv2/parcv2-lbu.S",

  # Store instructions

  "parcv1/parcv1-sw.S",
  "parcv2/parcv2-sh.S",
  "parcv2/parcv2-sb.S",

  # Unconditional jump instructions

  "parcv2/parcv2-j.S",
  "parcv1/parcv1-jal.S",
  "parcv1/parcv1-jr.S",
  "parcv2/parcv2-jalr.S",

  # Conditional branch instructions

  "parcv2/parcv2-beq.S",
  "parcv1/parcv1-bne.S",
  "parcv2/parcv2-blez.S",
  "parcv2/parcv2-bgtz.S",
  "parcv2/parcv2-bltz.S",
  "parcv2/parcv2-bgez.S",

]

#-------------------------------------------------------------------------
# Test function
#-------------------------------------------------------------------------
# This is the actual test function which is parameterized by the list of
# assembly tests. It will compile the assembly test, then use the elf
# reader to read the test into a sparse memory image, load the sparse
# memory image into the PISA simulator, and then run the simulation.

@pytest.mark.parametrize( "asm_test", asm_tests )
def test( tmpdir, asm_test ):

  # Derive the assembly file name and the desired binary name

  asm_dir_name  = os.path.dirname(__file__) + "/../tests"
  asm_base_name = os.path.basename( asm_test )
  exe_file_name = os.path.splitext( asm_base_name )[0]
  exe_file_name_wdir = str(tmpdir) + "/" + exe_file_name

  # Create an appropriate command to compile the assembly test

  maven_gcc_cmd = \
    "maven-gcc -nostartfiles" \
    " -T {asm_dir_name}/scripts/test.ld" \
    " -o {exe_file_name_wdir}" \
    " {asm_dir_name}/{asm_test}" \
    .format(**locals())

  print maven_gcc_cmd

  # Run the cross-compiler to generate the elf file

  subprocess.call( maven_gcc_cmd, shell=True )

  # Use the elf reader to read the assembly test into a memory image

  mem_image = None
  with open(exe_file_name_wdir,'rb') as file_obj:
    mem_image = elf.elf_reader( file_obj )

  # Construct the PISA simulator and run program

  sim = PisaSim( test_en=False, trace_en=True )
  sim.load( mem_image )
  sim.run()

  # Verify that the return value is one

  assert sim.return_value.uint() == 1

