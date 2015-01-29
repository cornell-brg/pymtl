from TestRandomDelay     import TestRandomDelay
from TestSource          import TestSource
from TestSink            import TestSink
from TestNetSink         import TestNetSink

from TestVectorSimulator import TestVectorSimulator
from TestSrcSinkSim      import TestSrcSinkSim

from TestMemory          import TestMemory
from TestProcManager     import TestProcManager
from SparseMemoryImage   import SparseMemoryImage

#-------------------------------------------------------------------------
# mk_test_case_table
#-------------------------------------------------------------------------

import collections

def mk_test_case_table( raw_test_case_table ):

  test_param_names = raw_test_case_table[0]

  TestCase = collections.namedtuple("TestCase",test_param_names)

  ids = []
  test_cases = []
  for row in raw_test_case_table[1:]:
    ids.append( row[0] )
    test_cases.append( TestCase(*row[1:]) )

  return {
    'ids'      : ids,
    'argnames' : ('test_params'),
    'argvalues' : test_cases,
  }

