#=========================================================================
# vc Subpackage
#=========================================================================

vc_deps =

vc_srcs = \
  vc-Test.v \
  vc-TestSource.v \
  vc-TestSink.v \
  vc-TestTagSink.v \
  vc-TestRandDelay.v \
  vc-TestRandDelaySource.v \
  vc-TestRandDelaySink.v \
  vc-TestRandDelayTagSink.v \
  vc-TestMemReqRespPort.v \
  vc-TestSinglePortMem.v \
  vc-TestSinglePortRandDelayMem.v \
  vc-TestDualPortMem.v \
  vc-TestDualPortRandDelayMem.v \
  vc-TestQuadPortMem.v \
  vc-TestQuadPortRandDelayMem.v \
  vc-TestOctoPortMem.v \
  vc-TestOctoPortRandDelayMem.v \
  vc-TestDecaPortMem.v \
  vc-TestDecaPortRandDelayMem.v \
  vc-TestIcosaPortMem.v \
  vc-Misc.v \
  vc-Muxes.v \
  vc-Arith.v \
  vc-StateElements.v \
  vc-Regfiles.v \
  vc-RAMs.v \
  vc-SRAMs.v \
  vc-Queues.v \
  vc-Arbiters.v \
  vc-Trace.v \
  vc-MemReqMsg.v \
  vc-MemReqMsgTag.v \
  vc-MemRespMsg.v \
  vc-MemRespMsgTag.v \
  vc-NetMsg.v \
  vc-NetMemAdapter.v \
  vc-ProcNetAdapter.v \
  vc-SyscMsg.v \
  vc-PriorityEncoder.v \
  vc-MemPortWidthAdapter.v \

vc_test_srcs = \
  vc-TestSink.t.v \
  vc-TestTagSink.t.v \
  vc-TestRandDelay.t.v \
  vc-TestRandDelaySource.t.v \
  vc-TestRandDelaySink.t.v \
  vc-TestRandDelayTagSink.t.v \
  vc-TestMemReqRespPort.t.v \
  vc-TestSinglePortMem.t.v \
  vc-TestSinglePortRandDelayMem.t.v \
  vc-TestDualPortMem.t.v \
  vc-TestDualPortRandDelayMem.t.v \
  vc-TestQuadPortMem.t.v \
  vc-TestQuadPortRandDelayMem.t.v \
  vc-TestOctoPortMem.t.v \
  vc-TestOctoPortRandDelayMem.t.v \
  vc-TestDecaPortMem.t.v \
  vc-TestDecaPortRandDelayMem.t.v \
  vc-TestIcosaPortMem.t.v \
  vc-Misc.t.v \
  vc-Muxes.t.v \
  vc-Arith.t.v \
  vc-StateElements.t.v \
  vc-Regfiles.t.v \
  vc-RAMs.t.v \
  vc-SRAMs.t.v \
  vc-Queues.t.v \
  vc-Arbiters.t.v \
  vc-MemReqMsg.t.v \
  vc-MemReqMsgTag.t.v \
  vc-MemRespMsg.t.v \
  vc-MemRespMsgTag.t.v \
  vc-NetMsg.t.v \
  vc-NetMemAdapter.t.v \
  vc-ProcNetAdapter.t.v \
  vc-SyscMsg.t.v \
  vc-PriorityEncoder.t.v \
  vc-MemPortWidthAdapter.t.v \

vc_prog_srcs = \

