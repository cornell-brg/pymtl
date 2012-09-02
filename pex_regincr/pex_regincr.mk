#=========================================================================
# Modular Python Build System Subproject Makefile Fragment
#=========================================================================

pex_regincr_deps = pymtl pmlib

pex_regincr_srcs = \
  RegIncrFlat.py \
  Register.py \
  Incrementer.py \
  RegIncrStruct.py \

pex_regincr_test_srcs = \
  RegIncrFlat_test.py \
  Register_test.py \
  Incrementer_test.py \
  RegIncrStruct_test.py \

pex_regincr_prog_srcs = \
  pex-regincr-sim \

