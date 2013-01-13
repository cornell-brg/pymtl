#=========================================================================
# Modular Python Build System Subproject Makefile Fragment
#=========================================================================

pmlib_deps = pymtl

pmlib_srcs = \
  TestVectorSimulator.py \
  TestSimpleSource.py \
  TestSimpleSink.py \
  TestRandomDelay.py \
  TestSource.py \
  TestSink.py \
  TestSimpleMemory.py \
  TestMemory.py \
  TestProcManager.py \
  TestMemManager.py \
  TestCacheResp32Sink.py \
	SparseMemoryImage.py \
	RegisterFile.py \
  PipeCtrl.py \
  TestNetSink.py \
  Crossbar.py \
  NormalQueue.py \
  valrdy.py \
  arith.py \
  muxes.py \
  regs.py \
  mem_msgs.py \
  queues.py \
  arbiters.py \
  net_msgs.py \
  adapters.py \

pmlib_test_srcs = \
  TestVectorSimulator_test.py \
  TestSimpleSink_test.py \
  TestRandomDelay_test.py \
  TestSource_test.py \
  TestSink_test.py \
  TestSimpleMemory_test.py \
  TestMemory_test.py \
  TestProcManager_test.py \
	SparseMemoryImage_test.py \
	RegisterFile_test.py \
  PipeCtrl_test.py \
  TestNetSink_test.py \
  Crossbar_test.py \
  NormalQueue_test.py \
  arith_test.py \
  muxes_test.py \
  regs_test.py \
  mem_msgs_test.py \
  queues_test.py \
  arbiters_test.py \
  net_msgs_test.py \
  adapters_test.py \

pmlib_vtest_srcs = \
  RegisterFile_v_test.py \
  queues_v_test.py \
  arbiters_v_test.py \

pmlib_prog_srcs = \

