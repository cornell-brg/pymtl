#=========================================================================
# test_utils
#=========================================================================
# Simple helper test functions.

from   pymtl       import *
import collections

#-------------------------------------------------------------------------
# mk_test_case_table
#-------------------------------------------------------------------------

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

#-------------------------------------------------------------------------
# run_test_vector_sim
#-------------------------------------------------------------------------

def run_test_vector_sim( model, test_vectors, dump_vcd=None, test_verilog=False ):

  # First row in test vectors contains port names

  port_names = test_vectors[0]

  # Remaining rows contain the actual test vectors

  test_vectors = test_vectors[1:]

  # Setup the model

  model.vcd_file = dump_vcd
  if test_verilog:
    model = get_verilated( model )
  model.elaborate()

  # Create a simulator

  sim = SimulationTool( model )

  # Reset model

  sim.reset()
  print ""

  # Run the simulation

  for row in test_vectors:

    # Apply test inputs

    for port_name, in_value in zip( port_names, row ):
      if port_name[-1] != "*":
        getattr( model, port_name ).value = in_value

    # Display line trace output

    sim.print_line_trace()

    # Check test outputs

    for port_name, ref_value in zip( port_names, row ):
      if port_name[-1] == "*":
        out_value = getattr( model, port_name[0:-1] )
        if ( ref_value != '?' ):
          assert out_value == ref_value

    # Tick the simulation

    sim.cycle()

  # Extra ticks to make VCD easier to read

  sim.cycle()
  sim.cycle()
  sim.cycle()



