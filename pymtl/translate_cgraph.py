#=========================================================================
# Verilog Translation Tool
#=========================================================================
"""Tool for translating ConnectionGraphs into Verilog HDL"""

from model import *
import sys

import inspect
from   translate_logic import PyToVerilogVisitor
from   translate_logic import FindRegistersVisitor
from   translate_logic import TemporariesVisitor

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
    print >> o, '\nmodule {}'.format( model.class_name )

    # Infer registers
    self.infer_regs( model, o )
    self.infer_temps( model, o )

    # Declare Ports
    if model.get_ports(): self.gen_port_decls( model.get_ports(), o )

    # Declare Localparams
    # TODO: remove localparams and just have wires instead?
    if model.get_localparams():
      self.gen_localparam_decls( model.get_localparams(), o )

    # Wires & Instantiations
    self.infer_implicit_wires( model, o )
    if model._wires: self.gen_wire_decls( model._wires, o )
    for submodule in model.get_submodules():
      self.gen_impl_wire_assigns( model, submodule, o )
      self.gen_module_insts( submodule, o )

    # Assignment Statments
    if model.get_ports(): self.gen_output_assigns( model, o )

    # Declare Wire Arrays
    if model._temparrays: self.gen_temparrays( model, o )

    # Declare Temporary Wires
    if model._tempwires: self.gen_temp_decls( model, o )

    # Declare Loop Variables
    if model._loopvars: self.gen_loopvar_decls( model, o )

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
    if node.parent != context and node.parent != None:
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
    w_type = 'reg ' if w.is_reg else 'wire'
    if w.width == 1:
      return "{} {};".format( w_type, w.verilog_name() )
    else :
      return "{} [{}:0] {};".format( w_type, w.width-1, w.verilog_name() )

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
    for m in target.get_submodules():
      print >> o, '\n  // {} wires'.format( m.name )
      for port in m.get_ports():
        wire_name = self.mk_impl_wire_name( m.name, port.name )
        # TODO: remove ImplicitWire?
        wire = ImplicitWire(wire_name, port.width)
        # TODO: HACKY
        wire.is_reg = (wire_name in target._tempregs)
        print >> o, '  {}'.format( self.wire_to_str(wire) )

  #-----------------------------------------------------------------------
  # Generate Local Parameter Declarations
  #-----------------------------------------------------------------------

  def gen_localparam_decls(self, params, o):
    """Generate Verilog source for parameter declarations."""
    print >> o, '\n  // localparams'
    for name, val in params:
      print >> o, '  localparam {0} = {1};'.format(name, val)

  #-----------------------------------------------------------------------
  # Generate Module Instances
  #-----------------------------------------------------------------------

  def gen_module_insts(self, submodule, o):
    """Generate Verilog source for instantiated submodules."""
    print >> o, ''
    print >> o, '  {} {}'.format( submodule.class_name, submodule.name )
    # TODO: add params
    print >> o, '  ('
    self.gen_port_insts( submodule.get_ports(), o )
    print >> o, '  );'

  #-----------------------------------------------------------------------
  # Generate Port Instances
  #-----------------------------------------------------------------------

  def gen_port_insts(self, ports, o):
    """Generate Verilog source for submodule port instances."""
    for p in ports[:-1]:
      wire_name = self.mk_impl_wire_name( p.parent.name, p.verilog_name() )
      print >> o , '    .{} ( {} ),'.format( p.verilog_name(), wire_name )
    p = ports[-1]
    wire_name = self.mk_impl_wire_name( p.parent.name, p.verilog_name() )
    print >> o, '    .{} ( {} )'.format( p.verilog_name(), wire_name )

  #-----------------------------------------------------------------------
  # Generate Assignments to Implicit Wires
  #-----------------------------------------------------------------------

  def gen_impl_wire_assigns(self, m, submodule, o):
    print >> o, '\n  // {} input assignments'.format( submodule.name )
    for port in submodule.get_inports():
      for edge in port.ext_connections:
        left  = self.mk_signal_str( edge.dest_node, edge.dest_slice, m )
        right = self.mk_signal_str( edge.src_node,  edge.src_slice,  m )
        print  >> o, "  assign {0} = {1};".format(left, right)

  #-----------------------------------------------------------------------
  # Generate Wire Declarations
  #-----------------------------------------------------------------------

  def gen_wire_decls(self, wires, o):
    """Generate Verilog source for wire declarations."""
    # TODO: test register inference
    print >> o, '\n  // explicit wires'
    for w in wires:

      # Declare the wire
      reg = 'reg' if w.is_reg else 'wire'
      if w.width == 1:
        print >> o, "  {} {};".format(reg, w.name)
      else :
        print >> o, "  {} [{}:0] {};".format(reg, w.width-1, w.name)

      # Print assignments
      # TODO: better way to do this?
      m = w.parent
      for edge in w.connections:
        if edge.is_dest( w ):
          left  = self.mk_signal_str( edge.dest_node, edge.dest_slice, m )
          right = self.mk_signal_str( edge.src_node,  edge.src_slice,  m )
          print  >> o, "  assign {0} = {1};".format(left, right)

    print >> o

  #-----------------------------------------------------------------------
  # Generate Temporary Arrays
  #-----------------------------------------------------------------------

  def gen_temparrays(self, model, o):
    """Generate Verilog source for temporaries used."""

    print >> o, '\n  // temporary arrays for port lists'
    for name in model._temparrays:
      port_list = model.__dict__[ name ]
      width  = port_list[0].width
      nports = len( port_list )
      # Declare the array
      t = 'reg' if isinstance( port_list[0], OutPort ) else 'wire'
      if width == 1:
        print >> o, "  %s %s [0:%d];" % (t, name, nports-1 )
      else :
        print >> o, "  %s [%d:0] %s [0:%d];" % (t, width-1, name, nports-1)
      # TODO: implement OutPort array assignments
      if   isinstance( port_list[0], InPort ):
        for i in range( nports ):
          print >> o, "  assign %s[%d] = %sIDX%d;" % (name, i, name, i)
      elif isinstance( port_list[0], OutPort ):
        for i in range( nports ):
          print >> o, "  assign %sIDX%d = %s[%d];" % (name, i, name, i)

      print >> o

  #-----------------------------------------------------------------------
  # Generate Temporary Declarations
  #-----------------------------------------------------------------------

  def gen_temp_decls(self, model, o):
    """Generate Verilog source for temporaries used."""
    print >> o, '\n  // temporaries'
    for name, w in model._tempwires.items():
      if w.width == 1:
        print >> o, "  reg %s;" % (w.name)
      else :
        print >> o, "  reg [%d:0] %s;" % (w.width-1, w.name)
    print >> o

  #-----------------------------------------------------------------------
  # Generate Loop Variable Declarations
  #-----------------------------------------------------------------------

  def gen_loopvar_decls(self, model, o):
    """Generate Verilog source for temporaries used."""
    print >> o, '  // loop variables'
    for name in model._loopvars:
      print >> o, "  integer {};".format( name )
    print >> o

  #-----------------------------------------------------------------------
  # Generate Assignments to Output Ports
  #-----------------------------------------------------------------------

  def gen_output_assigns(self, m, o):
    """Generate Verilog source for assignment statements."""
    print >> o, '\n  // output assignments'
    for port in m.get_outports():
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

    model_class = model.__class__
    src = inspect.getsource( model_class )
    tree = ast.parse( src )
    FindRegistersVisitor( model ).visit(tree)

  #-----------------------------------------------------------------------
  # Infer Temporaries
  #-----------------------------------------------------------------------

  def infer_temps(self, model, o):
    """Detect which wires/ports should be Verilog reg type."""

    model_class = model.__class__
    src = inspect.getsource( model_class )
    tree = ast.parse( src )
    TemporariesVisitor( model ).visit(tree)

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
    PyToVerilogVisitor( model, o ).visit( tree )

