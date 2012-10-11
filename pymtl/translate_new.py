#=========================================================================
# Verilog Translation Tool
#=========================================================================
"""Tool for translating ConnectionGraphs into Verilog HDL"""

from model import *
import sys
import collections

#------------------------------------------------------------------------
# Verilog Translation Tool
#-------------------------------------------------------------------------

class VerilogTranslationTool(object):

  #-----------------------------------------------------------------------
  # Constructor
  #-----------------------------------------------------------------------

  def __init__(self, model, o=sys.stdout):
    """Construct a Verilog translator from a MTL model.

    Parameters
    ----------
    model: an instantiated MTL model (Model).
    """
    # TODO: call elaborate on model?
    if not model.is_elaborated():
      msg  = "cannot initialize {0} tool.\n".format(self.__class__.__name__)
      msg += "Provided model has not been elaborated yet!!!"
      raise Exception(msg)

    self.to_translate = collections.OrderedDict()

    # Take either a string or a output stream
    if isinstance(o, str):
      o = open(o, 'w')

    # Find all the modules we need to translate in the hierarchy
    # TODO: use ordered list?
    self.collect_models( model )

    # Translate each Module Class
    for class_name, class_inst in self.to_translate.items():
      self.module_to_verilog( o, class_inst )

  #-----------------------------------------------------------------------
  # Collect Modules
  #-----------------------------------------------------------------------

  def collect_models(self, target):
    """Create an ordered set of all models we need to translate."""
    if not target.class_name in self.to_translate:
      self.to_translate[ target.class_name ] = target
      for m in target._submodules:
        self.collect_models( m )

  #-----------------------------------------------------------------------
  # Module to Verilog
  #-----------------------------------------------------------------------

  def module_to_verilog(self, o, target=None):
    """Generates Verilog source from a MTL model."""

    # Module declaration
    print >> o, '\nmodule %s' % target.class_name

    # Find registers
    #self.get_regs( target, o )

    # Declare Ports
    if target._ports: self.gen_port_decls( target._ports, o )

    ## Declare Localparams
    #if target._localparams: self.gen_localparam_decls( target._localparams, o )

    # Wires & Instantiations
    self.infer_impl_wires( target, o )
    #if target._wires: self.gen_wire_decls( target._wires, o )
    if target._submodules: self.gen_module_insts( target._submodules, o )

    ## Logic
    #self.gen_ast( target, o )

    # Assignment Statments
    if target._submodules: self.gen_impl_wire_assigns( target._submodules, o )
    if target._ports:      self.gen_output_assigns( target._ports, o )

    # End module
    print >> o, 'endmodule\n'


  #-----------------------------------------------------------------------
  # Generate Port Declarations
  #-----------------------------------------------------------------------

  def gen_port_decls(self, ports, o):
    """Generate Verilog source for port declarations."""
    print >> o, '('
    for p in ports[:-1]:
      print >> o , '  %s,' % self.port_to_str(p)
    p = ports[-1]
    print >> o, '  %s' % self.port_to_str(p)
    print >> o, ');'

  #-----------------------------------------------------------------------
  # Port To String
  #-----------------------------------------------------------------------

  def port_to_str(self, p):
    """Generate Verilog source for a port declaration."""
    reg = 'reg' if p.is_reg else ''
    if p.width == 1:
      return "%s %s %s" % (p.type, reg, p.verilog_name())
    else :
      return "%s %s [%d:0] %s" % (p.type, reg, p.width-1, p.verilog_name())

  #-----------------------------------------------------------------------
  # Wire To String
  #-----------------------------------------------------------------------

  def wire_to_str(self, w):
    """Generate Verilog source for a wire declaration."""
    if w.width == 1:
      return "wire %s;" % (w.verilog_name())
    else :
      return "wire [%d:0] %s;" % (w.width-1, w.verilog_name())

  #-----------------------------------------------------------------------
  # Implied Wire Name
  #-----------------------------------------------------------------------

  def mk_impl_wire_name( self, submodule_name, port_name ):
    return '{0}${1}'.format( submodule_name, port_name )

  #-----------------------------------------------------------------------
  # Infer Implied Wires
  #-----------------------------------------------------------------------

  def infer_impl_wires(self, target, o):
    """Creates a list of implied wire objects from connections in the MTL model.

    The MTL modeling framework allows you to make certain connections between
    ports without needing to explicitly declare intermediate wires. In some
    cases Verilog requires these wire declarations to be explicit. This utility
    method attempts to infer these implicit wires, generate ImplicitWire objects
    from them, and then add them to the connectivity lists of the necessary
    ports.
    """
    for m in target._submodules:
      for port in m._ports:
        wire_name = self.mk_impl_wire_name( m.name, port.verilog_name() )
        # TODO: remove ImplicitWire?
        wire = ImplicitWire(wire_name, port.width)
        print >> o, '  %s' % self.wire_to_str(wire)

  #-----------------------------------------------------------------------
  # Generate Module Instances
  #-----------------------------------------------------------------------

  def gen_module_insts(self, submodules, o):
    """Generate Verilog source for instantiated submodules."""
    for s in submodules:
      print >> o, ''
      print >> o, '  %s %s' % (s.class_name, s.name)
      # TODO: add params
      print >> o, '  ('
      self.gen_port_insts(s._ports, o)
      print >> o, '  );'

  #-----------------------------------------------------------------------
  # Generate Port Instances
  #-----------------------------------------------------------------------

  def gen_port_insts(self, ports, o):
    """Generate Verilog source for submodule port instances."""
    for p in ports[:-1]:
      #name = p.inst_connection.verilog_name() if p.inst_connection else ' '
      wire_name = self.mk_impl_wire_name( p.parent.name, p.verilog_name() )
      print >> o , '    .%s (%s),' % (p.verilog_name(), wire_name)
    p = ports[-1]
    #name = p.inst_connection.verilog_name() if p.inst_connection else ' '
    wire_name = self.mk_impl_wire_name( p.parent.name, p.verilog_name() )
    print >> o, '    .%s (%s)' % (p.verilog_name(), wire_name)

  #-----------------------------------------------------------------------
  # Generate Assignments to Implicit Wires
  #-----------------------------------------------------------------------

  def gen_impl_wire_assigns(self, submodules, o):
    for m in submodules:
      print >> o, ''
      input_ports  = [x for x in m._ports if isinstance(x,InPort)]
      output_ports = [x for x in m._ports if isinstance(x,OutPort)]
      for port in input_ports:
        for connect in port.ext_connections:
          left  = self.mk_impl_wire_name( m.name, connect.get_verilog_name( port ) )
          right = connect.other.verilog_name()
          print  >> o, "  assign {0} = {1};".format(left, right)
      for port in output_ports:
        for connect in port.ext_connections:
          left  = connect.other.verilog_name()
          right = self.mk_impl_wire_name( m.name, connect.get_verilog_name( port ) )
          print  >> o, "  assign {0} = {1};".format(left, right)

  #-----------------------------------------------------------------------
  # Generate Assignments to Output Ports
  #-----------------------------------------------------------------------

  def gen_output_assigns(self, ports, o):
    """Generate Verilog source for assignment statements."""
    output_ports = [x for x in ports if isinstance(x,OutPort)]
    for port in output_ports:
      # Note: multiple assigns should only occur on slicing
      output_assigns = port.int_connections
      for assign in output_assigns:
        # Don't connect to submodules, handled by gen_impl_wire_assigns
        if assign.other.parent == port.parent:
          left  = assign.get_verilog_name( port )
          right = assign.other.verilog_name()
          print  >> o, "  assign {0} = {1};".format(left, right)



