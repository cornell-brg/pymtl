#=========================================================================
# Modular Python Build System Subproject Makefile Fragment
#=========================================================================

pex_gcd_deps = pymtl pmlib

pex_gcd_srcs = \
  GcdUnitBL.py \
  GcdUnitRTL.py \

pex_gcd_test_srcs = \
  GcdUnitBL_test.py \
  GcdUnitRTL_test.py \

pex_gcd_vtest_srcs = \
  GcdUnitRTL_v_test.py \

pex_gcd_prog_srcs = \
  pex-gcd-sim \

