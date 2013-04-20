#=========================================================================
# Modular Python Build System Subproject Makefile Fragment
#=========================================================================

new_gcd_deps = pymtl pmlib

new_gcd_srcs = \
  GcdUnitBL.py \
  GcdUnitRTL.py \

new_gcd_test_srcs = \
  GcdUnitBL_test.py \
  GcdUnitRTL_test.py \

new_gcd_vtest_srcs = \
  GcdUnitRTL_v_test.py \

new_gcd_prog_srcs = \
  new-gcd-sim \

