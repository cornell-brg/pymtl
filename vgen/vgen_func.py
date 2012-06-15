import sys


def write_n(s):
  line = s.rstrip() + '\n'
  sys.stdout.write( line )
o = write_n

def port(porttype, name, size=None):
  if size:
    return '%s [%s-1:0] %s' % (porttype, size, name)
  else:
    return '%s %s' % (porttype, name)

def iport(name, size=1):
  return port('input ', name, size)

def oport(name, size=1):
  return port('output', name, size)

def ivalrdy(pfx, size=1):
  ports = [
      iport(pfx + '_val'),
      oport(pfx + '_rdy'),
      iport(pfx + '_msg', size),
    ]
  return ports

def ovalrdy(pfx, size=1):
  ports = [
      oport(pfx + '_val'),
      iport(pfx + '_rdy'),
      oport(pfx + '_msg', size),
    ]
  return ports

def cvalrdy(pfx):
  ports = [
      pfx + '_val',
      pfx + '_rdy',
      pfx + '_msg'
    ]
  return ports

def param_list(params):
  o('#(')
  for p,v in params[:-1]:
    #if not isinstance(p, str):
    #  print "ERROR: param type is not a string"
    #  sys.exit(-1)
    o('  parameter %s = %s,' % (p,v))
  p,v = params[-1]
  o('  parameter %s = %s' % (p,v))
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

