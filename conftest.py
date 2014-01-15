
def pytest_addoption(parser):
  parser.addoption( "--dump-vcd", action="store_true",
                    help="dump vcd for each test" )
  parser.addoption( "--dump-asm", action="store_true",
                    help="dump asm file for each test" )
  parser.addoption( "--dump-bin", action="store_true",
                    help="dump binary file for each test" )
  parser.addoption( "--test-verilog", action="store_true",
                    help="run verilog translation" )

def pytest_funcarg__dump_vcd(request):
  """Dump VCD for each test."""
  return request.config.option.dump_vcd

def pytest_funcarg__dump_asm(request):
  """Dump Assembly File for each test."""
  return request.config.option.dump_asm

def pytest_funcarg__dump_bin(request):
  """Dump Binary File for each test."""
  return request.config.option.dump_bin

def pytest_funcarg__test_verilog(request):
  """Test Verilog translation rather than python."""
  return request.config.option.test_verilog

def pytest_cmdline_preparse(config, args):
  """Don't write *.pyc and __pycache__ files."""
  import sys
  sys.dont_write_bytecode = True

import pytest
def pytest_runtest_setup(item):
  test_verilog = item.config.option.test_verilog
  if test_verilog and 'test_verilog' not in item.funcargnames:
    pytest.skip("ignoring non-Verilog tests")

