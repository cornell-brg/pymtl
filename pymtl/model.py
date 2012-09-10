#=========================================================================
# Model
#=========================================================================

"""Base modeling components for constructing hardware description models.

This module contains a collection of classes that can be used to construct MTL
(pronounced metal) models. Once constructed, a MTL model can be leveraged by
a number of tools for various purposes (simulation, translation into HDLs, etc).
"""
from connect import *

#-------------------------------------------------------------------------
# Port
#-------------------------------------------------------------------------

class Port(object):

  """Hidden base class implementing a module port."""

  def __init__(self, type, width, name='???'):
    """Constructor for a Port object.

    Parameters
    ----------
    type: string indicated whether this is an 'input' or 'output' port.
    width: bitwidth of the port.
    name: (TODO: remove? Previously only used for intermediate values).
    str: initializes a Port given a string containing a  port
         declaration. (TODO: remove. Only used by From.)
    """
    self.node   = Node(width)
    self.type   = type  # TODO: remove me
    self.width  = width
    self.name   = name
    self.parent = None
    # Connections used by Simulation Tool
    self.connections     = []
    # Connections used by VerilogTranslationTool
    # TODO: merge these different types of connections?
    self.inst_connection = None
    # Connections defined inside a module implementation
    self.int_connections = []
    # Connections defined when instantiating a model
    self.ext_connections = []
    # Needed by VerilogTranslationTool
    self.is_reg = False

  def __getitem__(self, addr):
    """Bitfield access ([]). Returns a Slice object."""
    return self.node[addr]

  def connect(self, target):
    """Creates a connection with a Port or Slice."""
    self.node.connect( target.node )

  @property
  def value(self):
    """Access the value on this port."""
    return self.node.value
  @value.setter
  def value(self, value):
    self.node.value = value

  @property
  def next(self):
    """Access the shadow value on this port, used for sequential logic."""
    return self.node.next
  @next.setter
  def next(self, value):
    self.node.next = value

  @property
  def name(self):
    """Access the name of this port."""
    # TODO: put name in Node or keep in Port?
    return self.node.name
  @name.setter
  def name(self, name):
    self.node.name = name

  @property
  def parent(self):
    """Access the parent of this port."""
    # TODO: put parent in Node or keep in Port?
    return self.node.parent
  @parent.setter
  def parent(self, parent):
    self.node.parent = parent

  # TODO: temporary hack for VCD
  @property
  def _code(self):
    """Access the parent of this port."""
    return self.node._code
  @_code.setter
  def _code(self, code):
    self.node._code = code

#-------------------------------------------------------------------------
# InPort
#-------------------------------------------------------------------------

class InPort(Port):
  """User visible implementation of an input port."""

  def __init__(self, width):
    """Constructor for an InPort object.

    Parameters
    ----------
    width: bitwidth of the port.
    """
    super(InPort, self).__init__('input', width)

#-------------------------------------------------------------------------
# OutPort
#-------------------------------------------------------------------------

class OutPort(Port):

  """User visible implementation of an output port."""

  def __init__(self, width):
    """Constructor for an OutPort object.

    Parameters
    ----------
    width: bitwidth of the port.
    """
    super(OutPort, self).__init__('output', width)

#-------------------------------------------------------------------------
# Wire
#-------------------------------------------------------------------------

class Wire(Port):

  """User visible implementation of a wire."""

  def __init__(self, width):
    """Constructor for an Wire object.

    Parameters
    ----------
    width: bitwidth of the wire.
    """
    super(Wire, self).__init__('wire', width)

#-------------------------------------------------------------------------
# Constant
#-------------------------------------------------------------------------

class Constant(object):

  """Hidden class for storing a constant valued node."""

  def __init__(self, value, width):
    """Constructor for a Constant object.

    Parameters
    ----------
    value: value of the constant.
    width: bitwidth of the constant.
    """
    self._value = Bits( width, value )
    self.width  = width
    self.type   = 'constant'
    self.name   = "%d'd%d" % (self.width, self._value.uint)
    self.parent = None
    # TODO: hack to ensure Constants can be treated as either port or node
    self.node  = self
    self.connections = []

  @property
  def value(self):
    """Access the value of this constant. Read only!"""
    return self._value

  def update(self, caller):
    pass

#-------------------------------------------------------------------------
# ImplicitWire
#-------------------------------------------------------------------------
# TODO: remove?

class ImplicitWire(object):

  """Hidden class to represent wires implicitly generated from connections."""

  def __init__(self, name, width):
    """Constructor for a ImplicitWire object.

    Parameters
    ----------
    name: name of the wire.
    width: bitwidth of the wire.
    """
    self.name  = name
    self.width = width
    self.type  = "wire"

#-------------------------------------------------------------------------
# Model
#-------------------------------------------------------------------------
# TODO: where to put exceptions?
class LogicSyntaxError(Exception):
  pass

class Model(object):

  """User visible base class for hardware models.

  Provides utility classes for elaborating connectivity between components,
  giving instantiated subcomponents proper names, and building datastructures
  that can be leveraged by various MTL tools.

  Any user implemented model that wishes to make use of the various MTL tools
  should subclass this.
  """

  def elaborate(self):
    self.model_classes = set()
    self.recurse_elaborate(self, 'top')
    self.recurse_connections()
    for c in self.model_classes:
      import inspect, ast
      src = inspect.getsource( c.__class__ )
      tree = ast.parse( src )
      accesses = set()
      CheckSyntaxVisitor(accesses).visit(tree)
      for a in accesses:
        if a[0] in vars(c):
          ptr = c.__getattribute__( a[0] )
          # Check InPort vs OutPort?
          if   isinstance( ptr, (Port,Wire) ) and a[1] == 'wr_value':
            raise LogicSyntaxError("Writing .value in an @posedge_clk block!")
          elif isinstance( ptr, (Port,Wire) ) and a[1] == 'wr_next':
            raise LogicSyntaxError("Writing .next in an @combinational block!")
          elif isinstance( ptr, (Port,Wire) ) and a[1] == 'rd_next':
            raise LogicSyntaxError("Reading .next inside logic block not allowed!")
          elif isinstance( ptr, (Port,Wire) ) and a[1] == False:
            print "WARNING: reading from Port without .value.",
            print "Module: {0}  Port: {1}".format( c.class_name, ptr.name)

  def recurse_elaborate(self, target, iname):
    """Elaborate a MTL model (construct hierarchy, name modules, etc.).

    The elaborate() function must be called on an instantiated toplevel module
    before it is passed to any MTL tools!
    """
    # TODO: call elaborate() in the tools?
    # TODO: better way to set the name?
    self.model_classes.add( target )
    target.class_name = target.__class__.__name__
    target.parent = None
    target.name = iname
    target.clk   = InPort(1)
    target.reset = InPort(1)
    target._exe_seq_logic  = False
    target._exe_comb_logic = False
    target._line_trace_en  = False
    target._wires = []
    target._ports = []
    target._submodules = []
    target._senses = []
    target._localparams = []
    # TODO: do all ports first?
    # Get the names of all ports and submodules
    for name, obj in target.__dict__.items():
      if not name.startswith('_'):
        self.check_type(target, name, obj)

  def check_type(self, target, name, obj):
    """Utility method to specialize elaboration actions based on object type."""
    # If object is a port, add it to our ports list
    if isinstance(obj, Port):
      obj.name = name
      obj.parent = target
      target._ports += [obj]
      if obj.type == 'input':
        target._senses += [obj]
    elif isinstance(obj, Wire):
      obj.name = name
      obj.parent = target
      target._wires += [obj]
      target._senses += [obj]
    # If object is a submodule, add it to our submodules list and recursively
    # call elaborate() on it
    elif isinstance(obj, Model):
      # TODO: change obj.type to obj.inst_type?
      obj.type = obj.__class__.__name__
      self.recurse_elaborate( obj, name )
      obj.parent = target
      connect( obj.clk, obj.parent.clk )
      connect( obj.reset, obj.parent.reset )
      target._submodules += [obj]
      # Add all the output ports of the child module to our sensitivity list
      target._senses += [ x for x in obj._ports if isinstance(x, OutPort) ]
    # We've found a constant assigned to a global variable.
    # TODO: add support for floats?
    elif isinstance(obj, int):
      target._localparams += [(name, obj)]
    # If the object is a list, iterate through each item in the list and
    # recursively call the check_type() utility function
    elif isinstance(obj, list):
      for i, item in enumerate(obj):
        item_name = "%s_%d" % (name, i)
        self.check_type(target, item_name, item)

  def recurse_connections(self):
    for port in self._ports:
      for c in port.node.connections:
        # If we're connected to a Constant, propagate it's value to all
        # indirectly connected Ports and Wires
        if isinstance(c, Constant):
          port.value = c.value
        # Do the same for Constants connected to Slices
        if isinstance(c, Slice) and isinstance(c.connections[0], Constant):
          assert len(c.connections) == 1
          c.value = c.connections[0].value
        # Otherwise, determine if the connected Wire/Port was connected in our
        # definition or during instantiation.  Used during VerilogTranslation.
        elif c.parent == port.parent or c.parent in self._submodules:
          port.int_connections += [c]
        else:
          port.ext_connections += [c]
    for submodule in self._submodules:
      submodule.recurse_connections()

  def is_elaborated(self):
    return hasattr(self, 'class_name')

  # Having a default line trace makes it easier to just always enable
  # line tracing in the test harness. -cbatten
  def line_trace(self):
    return ""

#------------------------------------------------------------------------
# Connect Functions
#------------------------------------------------------------------------

def connect( port_A, port_B):
  if   isinstance(port_B, int):
    port_A.connect( Constant(port_B, port_A.width) )
  elif isinstance(port_A, Slice):
    port_B.connect( port_A )
  else:
    port_A.connect( port_B )

_connect_ports = connect

def _connect_dict( connections ):
 for left_port,right_port in connections.iteritems():
   connect( left_port, right_port )

def connect( left, right=None ):
 if type(left) == dict:
   _connect_dict( left )
 else:
   _connect_ports( left, right )

#------------------------------------------------------------------------
# Visitors
#------------------------------------------------------------------------

import ast, _ast
class CheckSyntaxVisitor(ast.NodeVisitor):
  """Hidden class checking the validity of port and wire accesses.

  In order to translate synchronous @posedge_clk blocks into Verilog, we need
  to declare certain wires as registers.  This visitor looks for all ports
  written in @posedge_clk blocks so they can be declared as reg types.

  TODO: factor this and SensitivityListVisitor into same file?
  """
  def __init__(self, accesses):
    """Construct a new SensitivityListVisitor."""
    self.accesses = accesses
    self.decorator = None

  def visit_FunctionDef(self, node):
    """Visit all functions, but only parse those with special decorators."""
    if not node.decorator_list:
      return
    elif node.decorator_list[0].id in ['posedge_clk', 'combinational']:
      # Visit each line in the function, translate one at a time.
      self.decorator = node.decorator_list[0].id
      for x in node.body:
        self.visit(x)
      self.decorator = None

  def visit_Attribute(self, node):
    """Visit all attributes, convert into Verilog variables."""
    #target_name, debug = self.get_target_name(node)
    if self.decorator:
      target_name, debug = self.get_target_name(node)
      if  self.decorator == 'posedge_clk' and debug == 'value':
        self.accesses.add( (target_name, 'rd_'+debug, node.lineno) )
      elif self.decorator == 'combinational' and debug == 'next':
        self.accesses.add( (target_name, 'rd_'+debug, node.lineno) )
      else:
        self.accesses.add( (target_name, debug, node.lineno) )

  def visit_Assign(self, node):
    """Visit all assigns, searches for synchronous (registered) stores."""
    # Only works for one lefthand target
    assert len(node.targets) == 1
    target = node.targets[0]
    target_name, debug = self.get_target_name(target)
    # We are writing value inside of a posedge_clk, raise exception
    if   self.decorator == 'posedge_clk' and debug == 'value':
      self.accesses.add( (target_name, 'wr_'+debug, node.lineno) )
    # We are writing next inside of a combinational, raise exception
    elif self.decorator == 'combinational' and debug == 'next':
      self.accesses.add( (target_name, 'wr_'+debug, node.lineno) )
    self.visit( node.value )

  def get_target_name(self, node):
    # Is this an attribute? Follow it until we find a Name.
    name = []
    while isinstance(node, _ast.Attribute):
      name += [node.attr]
      node = node.value
    # Subscript, do nothing
    if isinstance(node, _ast.Subscript):
      return None, False
    # We've found the Name.
    assert isinstance(node, _ast.Name)
    name += [node.id]
    # If the target does not access .value or .next, tell the code to ignore it.
    if name[0] in ['value', 'next']:
      return '.'.join( name[::-1][1:-1] ), name[0]
    else:
      return name[0], False

#------------------------------------------------------------------------
# Decorators
#------------------------------------------------------------------------
# Normally a decorator returns a wrapped function, but here we return
# func unmodified.  We only use the decorator as a flag for the ast
# parsers.

def combinational(func):
  return func

def posedge_clk(func):
  return func

