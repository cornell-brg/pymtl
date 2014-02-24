def string_size(string, size):
  if( len(string) <= size or size == -1 ):
  return string
  else:
  return string[0:size] + "..."
  
def print_ports(model, out, prefix, size):
  in_ports = model.get_inports()
  length = 0
  for p in in_ports:
    temp_length = len(string_size(getattr(p,'name'),size))
    if(temp_length > length):
      length = temp_length
      
  out_ports = model.get_outports()
  length = max(length,10)
  length = length + 1
  
  print >> out, "\n" + prefix + "In Ports".ljust(length), "  Out Ports"
  old_prefix = prefix
  prefix = prefix + "| "
  if(len(out_ports) > len(in_ports)):
    list_length = len(in_ports)
    leftover_ports = out_ports
    pad = "".rjust(length+1)
  else:
    list_length = len(out_ports)
    leftover_ports = in_ports
    pad = ""
  
  x = 0
  while( x < list_length):
    print >> out, prefix + string_size(getattr(in_ports[x],'name').ljust(length),size),
    print >> out, string_size(getattr(out_ports[x],'name'),size)
    x = x + 1
  while(x < len(leftover_ports)):
    print >> out, pad + prefix + string_size(getattr(leftover_ports[x],'name'),size)
    x = x + 1
    
  print >> out, old_prefix + "END PORTS of " + getattr(model, 'name') +"\n"
  
def print_hierarchy_helper(model, out, show_ports, prefix, depth, max_depth,size):

  if(show_ports):
    print_ports(model,out,prefix,size)
  if(depth == max_depth):
    return
  
  
  sub_modules = model.get_submodules()
  for m in sub_modules:
    print >> out, prefix + string_size(getattr(m, 'name'),size) + " of type " + string_size(m.class_name,size)
    print_hierarchy_helper(m, out, show_ports, prefix + "  ", depth + 1, max_depth,size)
     
def print_hierarchy(model, out = sys.stdout, show_ports = False, max_depth = -1,size = 20):
  print >> out, "\n" + string_size(getattr(model, 'name'),10) + " of type " + string_size(model.class_name,10)
  print_hierarchy_helper(model,out,show_ports,"  ",0,max_depth,size)