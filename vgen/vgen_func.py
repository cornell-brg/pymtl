import sys


def write_n(s):
  line = s.rstrip() + '\n'
  sys.stdout.write( line )
o = write_n

def port(porttype, name, width=1):
  if width > 1:
    return '%s [%d-1:0] %s' % (porttype, width, name)
  else:
    return '%s %s' % (porttype, name)

def iport(name, width=1):
  return port('input ', name, width)

def oport(name, width=1):
  return port('output', name, width)

def ivalrdy(pfx, width=1):
  ports = [
      iport(pfx + '_val'),
      oport(pfx + '_rdy'),
      iport(pfx + '_msg', width),
    ]
  return ports

def ovalrdy(pfx, width=1):
  ports = [
      oport(pfx + '_val'),
      iport(pfx + '_rdy'),
      oport(pfx + '_msg', width),
    ]
  return ports

def param_list(params):
  o('#(')
  for p in params[:-1]:
    if not isinstance(p, str):
      print "ERROR: param type is not a string"
      sys.exit(-1)
    o('  parameter %s,' % p)
  o('  %s' % params[-1])
  o(')')

def port_list(ports):
  o('(')
  for p in ports[:-1]:
    if not isinstance(p, str):
      print "ERROR: port type is not a string"
      sys.exit(-1)
    o('  %s,' % p)
  o('  %s' % ports[-1])
  o(');')

def create_module(name, logic=None, ports=None, params=None):
  # Module Name
  o('module %s        ' % name )
  # Declare Params
  if params: param_list( params )
  # Declare Ports
  if ports:  port_list( ports )
  # Wires & Instantiations
  if logic:  print logic.getvalue(),
  # End module
  o('endmodule        ')


def main():
  ports = [
        port('input',  'a'),
        port('input',  'b'),
        port('output', 'out'),
      ]
  create_module('vgen-Adder', ports)

if __name__ == "__main__":
    main()

