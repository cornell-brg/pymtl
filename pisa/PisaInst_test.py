#=========================================================================
# PisaInst_test.py
#=========================================================================
# To test accessing instruction fields.

from PisaInst import PisaInst
from pisa_encoding import assemble_inst
import pytest

#-------------------------------------------------------------------------
# test_fields_reg
#-------------------------------------------------------------------------

def test_fields_reg():

  inst = PisaInst( assemble_inst( {}, 0, "addu r1, r2, r3" ) )
  assert inst.name == "addu"
  assert inst.rd   == 1
  assert inst.rs   == 2
  assert inst.rt   == 3

#-------------------------------------------------------------------------
# test_fields_imm
#-------------------------------------------------------------------------

def test_fields_imm():

  inst = PisaInst( assemble_inst( {}, 0, "addiu r30, r31, 0x4eef" ) )
  assert inst.name == "addiu"
  assert inst.rt   == 30
  assert inst.rs   == 31
  assert inst.imm  == 0x4eef

#-------------------------------------------------------------------------
# test_fields_shamt
#-------------------------------------------------------------------------

def test_fields_shamt():

  inst = PisaInst( assemble_inst( {}, 0, "sll r15, r16, 31" ) )
  assert inst.name  == "sll"
  assert inst.rd    == 15
  assert inst.rt    == 16
  assert inst.shamt == 31

#-------------------------------------------------------------------------
# test_fields_jtarg
#-------------------------------------------------------------------------

def test_fields_jtarg():

  inst_bits = assemble_inst( {"label":0x1010}, 0x1000, "j label" )
  inst = PisaInst( inst_bits )
  assert inst.name  == "j"
  assert inst.jtarg == 0x00404

