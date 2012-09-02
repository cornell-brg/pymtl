
def pytest_addoption(parser):
  parser.addoption( "--dump-vcd", action="store_true",
                    help="dump vcd for each test" )

def pytest_funcarg__dump_vcd(request):
  """Dump VCD for each test."""
  return request.config.option.dump_vcd

