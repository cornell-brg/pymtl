#=========================================================================
# Modular Python Build System Subproject Makefile Fragment
#=========================================================================

pex_dac_deps = pymtl pmlib

pex_dac_srcs = \
  InputTermCtrl.py \
  InputColCtrl.py \
  InputRowCtrl.py \
  OutputCtrl.py \
  RouteCompute.py \
  TorusRouter.py \
  Torus.py \

pex_dac_test_srcs = \
  TorusRouter_test.py \
  Torus_test.py \

pex_gcd_vtest_srcs = \
  Counter_v_test.py \
  RouteCompute_v_test.py \

pex_dac_prog_srcs = \
  pex-dac-sim \
