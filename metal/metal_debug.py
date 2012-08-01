import metal_model

def port_walk(tgt, spaces=0):
  for x in tgt.ports:
    print spaces*' ', x.parent.name, x
    for y in x.connections:
      fullname = y.name
      if y.parent:
        fullname = y.parent.name+'.'+fullname
      print spaces*' ', '   knctn: {0} {1}'.format(type(y), fullname)
    print spaces*' ', '   value:', x._value, #x.value
    if isinstance(x._value, metal_model.Slice):
      # TODO: handle this case in VerilogSlice instead?
      if x._value._value:
        print x.value
      else:
        print None
      print (spaces+1)*' ', '   slice:', x._value._value, bin(x._value.pmask)
    # TODO: handle this case in VerilogSlice instead?
    else:
      print x.value
  print
  for x in tgt.submodules:
    print spaces*' ', x.name
    port_walk(x, spaces+3)
