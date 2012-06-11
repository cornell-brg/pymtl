from vgen_func import ivalrdy, ovalrdy, create_module

num_mem_ports = 2

def req_resp_port(data_width, i=0):
  req_pfx = 'memreq%d'  % i
  rsp_pfx = 'memrsp%d' % i
  req_sz  = data_width
  rsp_sz  = data_width
  ports = []
  ports += ivalrdy(req_pfx, req_sz)
  ports += ovalrdy(rsp_pfx, rsp_sz)
  return ports


import StringIO
o = StringIO.StringIO()

def p_inst(params):
  for p,v in params[:-1]:
    print >> o, '    .%s (%s),' % (p,v)
  p,v = params[-1]
  print >> o, '    .%s (%s)' % (p,v)

def instantiate_module(module, inst_name, connections, params=None):
  """connections should take (port, wire) tuples,
     params should take (param, value) tuples.
  """
  # Module Name
  if not params:
    print >> o, '  %s %s' % (module, inst_name)
  else:
    print >> o, '  %s#(' % module
    param_inst(params)
    print >> o, '  %s' % inst_name
  print >> o, '  ('
  p_inst(connections)
  print >> o, '  );'


def n_port_mem(num_mem_ports, width):
  name = 'vgen_Magic%dPortMem' % num_mem_ports

  # Instantiate modules
  ports = []
  ports = [('in', 'wire1'), ('out', 'wire2')]
  instantiate_module('vc_TestReqRespMemPort', 'v1', ports)

  # Generate top level module
  ports = []
  for i in range(num_mem_ports):
    ports += req_resp_port(width, i)
  create_module(name, o, ports)


n_port_mem(2,  16)
#n_port_mem(10,  8)
