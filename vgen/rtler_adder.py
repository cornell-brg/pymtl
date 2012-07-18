import sys

from rtler_vbase import *
import ast, _ast

#  Target:
#
#  class FullAdder (foo):
#
#   def __init__(self):
#     self.in0  = InputPort(1)
#     self.in1  = InputPort(1)
#     self.cin  = InputPort(1)
#     self.sum  = OutputPort(1)
#     self.cout = OutputPort(1)
#
#  class RippleCarryAdder (foo):
#
#   def __init__(self):
#     self.in0  = InputPort(32)
#     self.in1  = InputPort(32)
#     self.sum  = OutputPort(32)
#
#   def elaborate(self):
#
#     self.adders = [ FullAdder() for i in xrange(32) ]
#
#     for i in xrange(32):
#       self.adders[i].in0 <> self.in0[i]
#       self.adders[i].in1 <> self.in1[i]
#       self.adders[i].out <> self.out[i]
#
#     self.adders[0].cin.wr(0)
#     for i in xrange(31):
#       self.adders[i+1].cin <> self.adders[i].cout

import inspect
def always_comb(fn):
  def wrapped(self):
    #for x,y in inspect.getmembers(fn, inspect.isdatadescriptor):
    #  print x,y
    return fn(self)
  return wrapped

registry = set()
class SensitivityListVisitor(ast.NodeVisitor):
  # http://docs.python.org/library/ast.html#abstract-grammar
  def __init__(self):
    self.current_fn = None

  def visit_FunctionDef(self, node):
    """ Only parse functions that have the @... decorator! """
    #pprint.pprint( dir(node) )
    #print "Function Name:", node.name
    if not node.decorator_list:
      return
    decorator_names = [x.id for x in node.decorator_list]
    if 'tdec' in decorator_names:
      # Visit each line in the function, translate one at a time.
      for x in node.body:
        self.current_fn = node.name
        self.visit(x)
        self.current_fn = None

  # All attributes... only want names?
  #def visit_Attribute(self, node):
  def visit_Name(self, node):
    #pprint.pprint( dir(node.ctx) )
    #print node.id, type( node.ctx )
    if not self.current_fn:
      return
    if isinstance( node.ctx, _ast.Load ) and node.id != "self":
      print node.id, type( node.ctx )
      registry.add( (node.id, self.current_fn) )

import pprint
def tdec(fn):
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


class FullAdder(Synthesizable):
  def __init__(self):
    # Can't set the instance name during init, but can during elaboration
    # by walking the Top-Level Module's __dict__ and checking types
    self.in0  = InPort (1)
    self.in1  = InPort (1)
    self.cin  = InPort (1)
    self.sum  = OutPort(1)
    self.cout = OutPort(1)
    sim.add_callback(self.in0, self.logic)
    sim.add_callback(self.in1, self.logic)
    sim.add_callback(self.cin, self.logic)

  @always_comb
  @tdec
  def logic(self):
    in0 = self.in0
    in1 = self.in1
    cin = self.cin
    sum = self.sum
    cout = self.cout
    ##print "FUNC", "in0", in0.value, "in1", in1.value, "cin", cin.value
    sum  <<= (in0 ^ in1) ^ cin
    cout <<= (in0 & in1) | (in0 & cin) | (in1 & cin)
    #print "FUNC", "in0", in0.value, "in1", in1.value, "cin", cin.value


class AdderChain(Synthesizable):
  def __init__(self, depth):
    # Can't set the instance name during init, but can during elaboration
    # by walking the Top-Level Module's __dict__ and checking types
    self.in0  = InPort (1)
    self.in1  = InPort (1)
    self.sum  = OutPort(1)

    self.adders = [ FullAdder() for i in xrange(depth) ]
    self.adders[0].in0 <> self.in0
    self.adders[0].in1 <> self.in1
    self.adders[0].cin <> 0

    for i in xrange(1, depth):
      self.adders[i].in0 <> self.adders[i-1].sum
      self.adders[i].in1 <> 1
      self.adders[i].cin <> 0

    self.sum <> self.adders[-1].sum


class RippleCarryAdder(Synthesizable):
  def __init__(self, bits):
    self.in0 = InPort (bits)
    self.in1 = InPort (bits)
    self.sum = OutPort(bits)

    self.adders = [ FullAdder() for i in xrange(bits) ]

    for i in xrange(bits):
      self.adders[i].in0 <> self.in0[i]
      self.adders[i].in1 <> self.in1[i]
      self.adders[i].sum <> self.sum[i]

    for i in xrange(bits-1):
      self.adders[i+1].cin <> self.adders[i].cout
    self.adders[0].cin <> 0


x = FullAdder()
#def print_members(object):
#  print "ALL MEMBERS"
#  print "==========="
#  print "{0:20}  {1}".format("Type", "Object")
#  print "{0:20}  {1}".format("----", "------")
#  for m_type, m_object in inspect.getmembers(object):
#    print "{0:20}  {1}".format(m_type, m_object)
#  print
#  print "CLASSES"
#  print "======="
#  print "{0:20}  {1}".format("Type", "Object")
#  print "{0:20}  {1}".format("----", "------")
#  for m_type, m_object in inspect.getmembers(object, inspect.isclass):
#    print "{0:20}  {1}".format(m_type, m_object)
#print_members(x)

src = inspect.getsource( FullAdder )
tree = ast.parse( src )
SensitivityListVisitor().visit( tree )
print registry

#pprint.pprint( dir(x) )
#x.in0 = 1
#x.in1 = 0
#x.cin = 1
#x.logic()
#print x.sum, x.cout
