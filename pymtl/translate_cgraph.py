#=========================================================================
# Verilog Translation Tool
#=========================================================================
"""Tool for translating ConnectionGraphs into Verilog HDL"""

from model import *
import sys

import inspect
from   translate_logic import PyToVerilogVisitor
from   translate_logic import FindRegistersVisitor

#------------------------------------------------------------------------
# Verilog Translation Tool
#-------------------------------------------------------------------------

class ConnectionGraphToVerilog(object):

  #-----------------------------------------------------------------------
  # Constructor
  #-----------------------------------------------------------------------

  def __init__(self, model, o=sys.stdout):
    """Generates Verilog source from a MTL model."""

    # Module declaration
    print >> o, '//-{}'.format( 71*'-' )
    print >> o, '// {}'.format( model.class_name )
    print >> o, '//-{}'.format( 71*'-' )
    print >> o, 'module {}'.format( model.class_name )

    # Infer registers
    self.infer_regs( model, o )

    # Declare Ports
    if model._ports: self.gen_port_decls( model._ports, o )

    # Declare Localparams
    # TODO: remove localparams and just have wires instead?
    if model._localparams:
      self.gen_localparam_decls( model._localparams, o )

    # Wires & Instantiations
    self.infer_implicit_wires( model, o )
    #if model._wires: self.gen_wire_decls( model._wires, o )
    for submodule in model._submodules:
      self.gen_impl_wire_assigns( model, submodule, o )
      self.gen_module_insts( submodule, o )

    # Assignment Statments
    if model._ports: self.gen_output_assigns( model, o )

    # Logic
    self.gen_logic_blocks( model, o )

    # End module
    print >> o, 'endmodule\n'


  #-----------------------------------------------------------------------
  # Generate Port Declarations
  #-----------------------------------------------------------------------

  def gen_port_decls(self, ports, o):
    """Generate Verilog source for port declarations."""
    print >> o, '('
    for p in ports[:-1]:
      print >> o , '  {},'.format( self.port_to_str(p) )
    p = ports[-1]
    print >> o, '  {}'.format( self.port_to_str(p) )
    print >> o, ');'

  #-----------------------------------------------------------------------
  # Make Signal String
  #-----------------------------------------------------------------------

  def mk_signal_str(self, node, addr, context):
    """Generate Verilog source for a wire declaration."""
    # Special case constants
    if isinstance( node, Constant ):
      return node.name

    # If the node's parent module isn't the same as the current module
    # we need to prefix the signal name with the module name
    if node.parent != context:
      prefix = "{}$".format( node.parent.name )
    else:
      prefix = ""

    if isinstance( addr, slice ):
      suffix = "[{}:{}]".format( addr.stop - 1, addr.start )
    elif isinstance( addr, int ):
      suffix = "[{}]".format( addr )
    else:
      suffix = ""

    return prefix + node.name + suffix

  #-----------------------------------------------------------------------
  # Port To String
  #-----------------------------------------------------------------------

  def port_to_str(self, p):
    """Generate Verilog source for a port declaration."""
    reg = 'reg' if p.is_reg else ''
    if p.width == 1:
      return "{} {} {}".format(p.type, reg, p.verilog_name())
    else :
      return "{} {} [{}:0] {}".format(p.type, reg,
                                      p.width-1, p.verilog_name())

  #-----------------------------------------------------------------------
  # Wire To String
  #-----------------------------------------------------------------------

  def wire_to_str(self, w):
    """Generate Verilog source for a wire declaration."""
    if w.width == 1:
      return "wire {};".format( w.verilog_name() )
    else :
      return "wire [{}:0] {};".format( w.width-1, w.verilog_name() )

  #-----------------------------------------------------------------------
  # Implied Wire Name
  #-----------------------------------------------------------------------

  def mk_impl_wire_name( self, submodule_name, port_name ):
    return '{0}${1}'.format( submodule_name, port_name )

  #-----------------------------------------------------------------------
  # Infer Implied Wires
  #-----------------------------------------------------------------------

  def infer_implicit_wires(self, target, o):
    """Creates a list of implied wire objects from connections in the MTL model.

    The MTL modeling framework allows you to make certain connections between
    ports without needing to explicitly declare intermediate wires. In some
    cases Verilog requires these wire declarations to be explicit. This utility
    method attempts to infer these implicit wires, generate ImplicitWire objects
    from them, and then add them to the connectivity lists of the necessary
    ports.
    """
    for m in target._submodules:
      print >> o, '\n  // {} wires'.format( m.name )
      for port in m._ports:
        wire_name = self.mk_impl_wire_name( m.name, port.name )
        # TODO: remove ImplicitWire?
        wire = ImplicitWire(wire_name, port.width)
        print >> o, '  {}'.format( self.wire_to_str(wire) )

  #-----------------------------------------------------------------------
  # Generate Local Parameter Declarations
  #-----------------------------------------------------------------------

  def gen_localparam_decls(self, params, o):
    """Generate Verilog source for parameter declarations."""
    print >> o, '\n  // localparams'
    for name, val in params:
      print >> o, '  localparam {0} = {1};'.format(name, val)
    print >> o

  #-----------------------------------------------------------------------
  # Generate Module Instances
  #-----------------------------------------------------------------------

  def gen_module_insts(self, submodule, o):
    """Generate Verilog source for instantiated submodules."""
    print >> o, ''
    print >> o, '  {} {}'.format( submodule.class_name, submodule.name )
    # TODO: add params
    print >> o, '  ('
    self.gen_port_insts(submodule._ports, o)
    print >> o, '  );'

  #-----------------------------------------------------------------------
  # Generate Port Instances
  #-----------------------------------------------------------------------

  def gen_port_insts(self, ports, o):
    """Generate Verilog source for submodule port instances."""
    for p in ports[:-1]:
      wire_name = self.mk_impl_wire_name( p.parent.name, p.verilog_name() )
      print >> o , '    .{} ({}),'.format( p.verilog_name(), wire_name )
    p = ports[-1]
    wire_name = self.mk_impl_wire_name( p.parent.name, p.verilog_name() )
    print >> o, '    .{} ({})'.format( p.verilog_name(), wire_name )

  #-----------------------------------------------------------------------
  # Generate Assignments to Implicit Wires
  #-----------------------------------------------------------------------

  def gen_impl_wire_assigns(self, m, submodule, o):
    print >> o, '\n  // {} input assignments'.format( submodule.name )
    input_ports  = [x for x in submodule._ports if isinstance(x,InPort)]
    for port in input_ports:
      for edge in port.ext_connections:
        left  = self.mk_signal_str( edge.dest_node, edge.dest_slice, m )
        x = (submodule.parent != edge.src_node.parent)
        right = self.mk_signal_str( edge.src_node,  edge.src_slice,  m )
        print  >> o, "  assign {0} = {1};".format(left, right)

  #-----------------------------------------------------------------------
  # Generate Assignments to Output Ports
  #-----------------------------------------------------------------------

  def gen_output_assigns(self, m, o):
    """Generate Verilog source for assignment statements."""
    print >> o, '\n  // output assignments'
    ports = m._ports
    output_ports = [x for x in ports if isinstance(x,OutPort)]
    for port in output_ports:
      # Note: multiple assigns should only occur on slicing
      for edge in port.int_connections:
        left  = self.mk_signal_str( edge.dest_node, edge.dest_slice, m )
        right = self.mk_signal_str( edge.src_node,  edge.src_slice,  m )
        print  >> o, "  assign {0} = {1};".format(left, right)
    print >> o, ''

  #-----------------------------------------------------------------------
  # Infer Registers
  #-----------------------------------------------------------------------

  def infer_regs(self, model, o):
    """Detect which wires/ports should be Verilog reg type."""
    reg_stores = set()

    model_class = model.__class__
    src = inspect.getsource( model_class )
    tree = ast.parse( src )
    FindRegistersVisitor( reg_stores ).visit(tree)
    for reg_name in reg_stores:
      port_ptr = model.__getattribute__(reg_name)
      port_ptr.is_reg = True

  #-----------------------------------------------------------------------
  # Generate Combinational and Sequential Logic Blocks
  #-----------------------------------------------------------------------

  def gen_logic_blocks(self, model, o):
    """Generate Verilog source from decorated python functions.

    Currently supports the @combinational and @posedge_clk decorators.
    """
    model_class = model.__class__
    src = inspect.getsource( model_class )
    tree = ast.parse( src )
    #import debug_utils
    #debug_utils.print_ast( tree )
    PyToVerilogVisitor( o ).visit(tree)

