#=========================================================================
# Modular Python Build System Subproject Makefile Fragment
#=========================================================================

pex_sorter_deps = pymtl pmlib

pex_sorter_srcs = \
  SorterBL.py \
  SorterCL.py \
  SorterRTL.py \
  MinMax.py \
  SorterStruct.py \

pex_sorter_test_srcs = \
  SorterBL_test.py \
  SorterCL_test.py \
  SorterRTL_test.py \
  MinMax_test.py \
  SorterStruct_test.py \

pex_sorter_prog_srcs = \
  pex-sorter-sim

