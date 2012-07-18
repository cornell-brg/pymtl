import pprint

def print_members(object):
  print "ALL MEMBERS"
  print "==========="
  print "{0:20}  {1}".format("Type", "Object")
  print "{0:20}  {1}".format("----", "------")
  for m_type, m_object in inspect.getmembers(object):
    print "{0:20}  {1}".format(m_type, m_object)
  print
  print "CLASSES"
  print "======="
  print "{0:20}  {1}".format("Type", "Object")
  print "{0:20}  {1}".format("----", "------")
  for m_type, m_object in inspect.getmembers(object, inspect.isclass):
    print "{0:20}  {1}".format(m_type, m_object)

def port_walk(tgt, spaces=0):
  for x in tgt.ports:
    print spaces*' ', x.parent, x
    for y in x.connection:
      print spaces*' ', '   knctn:', type(y), y.parent, y.name
    print spaces*' ', '   value:', x._value, x.value
  print
  for x in tgt.submodules:
    print spaces*' ', x.name
    port_walk(x, spaces+3)

def inspect_dec(fn):
  #pprint.pprint(vars(fn))
  #pprint.pprint(locals())
  #pprint.pprint(globals())
  #pprint.pprint(dir(fn))
  #pprint.pprint(dir(fn.func_code))
  #pprint.pprint(inspect.getmembers(fn, inspect.isdatadescriptor))
  print fn.func_code.co_varnames
  print fn.func_code.co_names
  print fn.func_code.co_freevars
  #print fn.im_class  # Only works if you call on instance! Boo.
  return fn
