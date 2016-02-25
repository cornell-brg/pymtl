#=======================================================================
# Model.py
#=======================================================================
"""Base modeling components for building hardware description models.

This module contains a collection of classes that can be used to construct
PyMTL (pronounced py-metal) models. Once constructed, a PyMTL model can be
leveraged by a number of PyMTL tools for various purposes (simulation,
translation into HDLs, etc).
"""

from metaclasses    import MetaCollectArgs
from ConnectionEdge import ConnectionEdge, PyMTLConnectError
from signals        import Signal, InPort, OutPort, Wire, Constant
from signal_lists   import PortList, WireList
from PortBundle     import PortBundle
from ..datatypes    import Bits

#from physical      import PhysicalDimensions

import collections
import inspect
import warnings
import math

#=======================================================================
# Model
#=======================================================================
class Model( object ):
  """Base class for PyMTL hardware models.

  Provides utility classes for elaborating connectivity between
  components, giving instantiated subcomponents proper names, and
  building datastructures that can be leveraged by various tools.

  Any user implemented model that wishes to make use of the various
  PyMTL tools should subclass this.
  """

  __metaclass__ = MetaCollectArgs
  _debug        = False

  # The following set of options are useful for generating a black box
  # for this module when get translated to Verilog. For example, if you
  # want to incorporate a SRAM or some other hard IP you could have a
  # behavioral model in PyMTL for simulation, when pushed to the ASIC
  # flow it will be treated as a black box and can be linked to the
  # library of that SRAM or IP.

  # To use this feature, turn on enable_blackbox option of the
  # TranslationTool
  # for example: s.sram = TranslationTool( s.sram, enable_blackbox=True )

  vblackbox      = False  # Mark this module as a black box
  vbb_modulename = ""     # Use a custom module name for this black box
  vbb_no_reset   = False  # Do not generate reset port in Verilog
  vbb_no_clk     = False  # Do not generate clk   port in Verilog

  # Option: vannotate_arrays
  #
  # The following option allows annotation of an array when translating to
  # Verilog.
  #
  # For example, in order for FPGA synthesis tools to infer BRAM, the
  # array must be annotated like this:
  #
  #   (* RAM_STYLE="BLOCK" *) reg [p_col_width-1:0]  ram [31:0];
  #
  # The vannotate_arrays option is set up as a dict. Keys are the names of
  # the arrays to annotate, and values are annotation strings. For
  # example, generating the above annotation (before the 'reg' keyword)
  # looks like this:
  #
  #   vannotate_arrays = { 'ram': '(* RAM_STYLE="BLOCK" *)' }
  #

  vannotate_arrays = {}

  # Option: vmark_as_bram (inferring BRAM on FPGA)
  #
  # The following option marks the current Model as a BRAM and makes it
  # _easier_ for the FPGA tools to infer BRAM. Note that you still need to
  # check the synthesis report to make sure!
  #
  # Specifically, vmark_as_bram does the following:
  #
  # - suppress wire declarations. I.e., removes these declarations:
  #
  #     // wire declarations
  #     wire   [  31:0] ram$000;
  #     wire   [  31:0] ram$001;
  #
  # - suppress array declarations. I.e., removes these declarations:
  #
  #     // array declarations
  #     assign ram$000 = ram[  0];
  #     assign ram$001 = ram[  1];
  #
  # For some reason, wire/array declarations make the tools not infer
  # BRAM. We generate these so we can peek into the array in the VCD. We
  # will have to give that up to infer BRAM.
  #
  # Note: You should also add a vannotate_arrays annotation to hint that
  # the ram array should be a BRAM:
  #
  #   vannotate_arrays = { 'ram': '(* RAM_STYLE="BLOCK" *)' }
  #
  # See above for how to use vannotate_arrays.

  vmark_as_bram = False

  #=====================================================================
  # Modeling API
  #=====================================================================

  #---------------------------------------------------------------------
  # __new__
  #---------------------------------------------------------------------
  def __new__( cls, *args, **kwargs ):
    """Pre-constructor adds default 'clk' and 'reset' Signals to PyMTL.

    We use __new__ instead of __init__ for this purpose so that user's
    do not need to explicitly call the super constructor in their Model
    definitions: ``super( Model, self ).__init__()`` is too ugly!
    """

    # Instantiate a new Python object
    inst       = object.__new__( cls, *args, **kwargs )

    # Add implicit clk and reset ports
    inst.clk   = InPort( 1 )
    inst.reset = InPort( 1 )

    # Initialize internal datastructures
    inst._tick_blocks          = []
    inst._posedge_clk_blocks   = []
    inst._combinational_blocks = []
    inst._connections          = set()

    return inst

  #---------------------------------------------------------------------
  # connect
  #---------------------------------------------------------------------
  def connect( self, left_port, right_port ):
    """Structurally connect a Signal to another Signal or a constant, or
    two PortBundles with the same interface.

    Ports structurally connected with s.connect are guaranteed to have
    the same value during simulation:

    >>> s.connect( s.port_a, s.port_b )

    This works for slices as well:

    >>> s.connect( s.port_c[0:4], s.port_d[4:8] )

    A signal connected to a constant will be tied to that value:

    >>> s.connect( s.port_e, 8 )

    Several Signals can be structurally connected with a single
    statement by encapsulating them in PortBundles:

    >>> s.connect( s.my_bundle_a, s.my_bundle_b )
    """

    # Throw an error if connect() is used on two wires.
    if isinstance( left_port, Wire ) and isinstance( right_port, Wire ):
      e = ('Connecting two Wire signals is not supported!\n'
           'If you are certain this is something you really need to do, '
           'use connect_wire instead:\n\n '
           '  # translation will fail if directionality is wrong!!!\n'
           '  connect_wire( dest = <s.out>, src = <s.in_> )'
          )
      frame, filename, lineno, func_name, lines, idx = inspect.stack()[1]
      msg  = '{}\n\nLine: {} in File: {}\n>'.format( e, lineno, filename )
      msg += '>'.join( lines )
      raise PyMTLConnectError( msg )

    # Try to connect the two signals/portbundles
    try:
      if  isinstance( left_port, PortBundle ):
        self._connect_bundle( left_port, right_port )
      else:
        self._connect_signal( left_port, right_port )

    # Throw a helpful error on failure
    except PyMTLConnectError as e:
      frame, filename, lineno, func_name, lines, idx = inspect.stack()[1]
      msg  = '{}\n\nLine: {} in File: {}\n>'.format( e, lineno, filename )
      msg += '>'.join( lines )
      raise PyMTLConnectError( msg )

  #-----------------------------------------------------------------------
  # connect_pairs
  #-----------------------------------------------------------------------
  def connect_pairs( self, *connections ):
    """Structurally connect pairs of signals.

    This provides a more concise syntax for interconnecting large
    numbers of Signals by allowing the user to supply a series of signals
    which are to be connected pairwise.

    >>> s.connect_pairs(
    >>>   s.mod.a, s.a,
    >>>   s.mod.b, 0b11,
    >>>   s.mod.c, s.x[4:5],
    >>> )

    Alternatively, a list of signals can be created and passed in:

    >>> s.connect_pairs( *signal_list )

    """

    # Throw an error if user tries to connect an odd number of signals
    if len( connections ) & 1:
      e    = 'An odd number of signals were provided!'
      frame, filename, lineno, func_name, lines, idx = inspect.stack()[1]
      msg  = '{}\n\nLine: {} in File: {}\n>'.format( e, lineno, filename )
      msg += '>'.join( lines )
      raise PyMTLConnectError( msg )

    # Iterate through signals pairwise
    citer = iter( connections )
    for left_port, right_port in zip( citer, citer ):
      try:
        self.connect( left_port, right_port )

      # Throw a helpful error if any pairwise connection fails
      except PyMTLConnectError as e:
        frame, filename, lineno, func_name, lines, idx = inspect.stack()[1]
        msg  = '{}\n\nLine: {} in File: {}\n>'.format( e, lineno, filename )
        msg += '>'.join( lines )
        raise PyMTLConnectError( msg )

  #-----------------------------------------------------------------------
  # connect_dict
  #-----------------------------------------------------------------------
  def connect_dict( self, connections ):
    """Structurally connect Signals given a dictionary mapping.

    This provides a more concise syntax for interconnecting large
    numbers of Signals by using a dictionary to specify Signal-to-Signal
    connection mapping.

    >>> s.connect_dict({
    >>>   s.mod.a : s.a,
    >>>   s.mod.b : 0b11,
    >>>   s.mod.c : s.x[4:5],
    >>> })

    """

    for left_port, right_port in connections.iteritems():
      try:
        self.connect( left_port, right_port )

      # Throw a helpful error if any pairwise connection fails
      except PyMTLConnectError as e:
       frame, filename, lineno, func_name, lines, idx = inspect.stack()[1]
       msg  = '{}\n\nLine: {} in File: {}\n>'.format( e, lineno, filename )
       msg += '>'.join( lines )
       raise PyMTLConnectError( msg )

  #---------------------------------------------------------------------
  # connect_wire
  #---------------------------------------------------------------------
  def connect_wire( self, dest=None, src=None ):
    """Structurally connect two Wires where direction must be specified.

    Directly connecting two Wires is not encouraged in PyMTL modeling.
    Typically, intermediate Wire objects should not be needed for
    structural connectivity since Ports can be directly connected, and
    Wires are primarily intended for communicating values between
    behavioral blocks within a Model.

    If you are certain you want to structurally connect two Wires, you
    must use connect_wire() to explicitly specify the directionality.

    >>> s.connect_wire( dest = s.port_a, src = s.port_b )
    """

    self._connect_signal( src, dest )   # expects the src first

  #-----------------------------------------------------------------------
  # connect_auto
  #-----------------------------------------------------------------------
  def connect_auto( self, m1, m2 = None ):
    """EXPERIMENTAL. Try to connect all InPort and OutPorts with the
    same name between two models.

    Note that this is not heavily tested or stable, you probably don't
    want to use this...
    """

    if not hasattr( self, '_auto_connects' ):
      self._auto_connects = []
    self._auto_connects.append((m1,m2))

  #---------------------------------------------------------------------
  # tick_fl
  #---------------------------------------------------------------------
  def tick_fl( self, func ):
    """Decorator to mark a functional-level sequential function.

    Logic blocks marked with @s.tick_fl fire every clock cycle and may
    utilize components using the greenlet concurrency library. They are
    not Verilog translatable.

    >>> @s.tick_fl
    >>> def my_logic()
    >>>   s.out.next = s.in_
    """

    return self.tick( func )

  #---------------------------------------------------------------------
  # tick_cl
  #---------------------------------------------------------------------
  def tick_cl( self, func ):
    """Decorator to mark a cycle-level sequential logic.

    Logic blocks marked with @s.tick_cl fire every clock cycle. They
    cannot take advantage of greenlets-enabled library components, nor
    are they Verilog translatable.

    >>> @s.tick_cl
    >>> def my_logic()
    >>>   s.out.next = s.in_
    """

    return self.tick( func )

  #---------------------------------------------------------------------
  # tick_rtl
  #---------------------------------------------------------------------
  def tick_rtl( self, func ):
    """Decorator to mark register-transfer level sequential logic.

    Logic blocks marked with @s.tick_cl fire every clock cycle, and are
    meant to be Verilog translatable. Note that translation only works
    if a limited, translatable subset of Python is used.

    >>> @s.tick_rtl
    >>> def my_logic()
    >>>   s.out.next = s.in_
    """

    return self.posedge_clk( func )

  #---------------------------------------------------------------------
  # combinational
  #---------------------------------------------------------------------
  def combinational( self, func ):
    """Decorator to annotate an RTL combinational function.

    Logic blocks marked with @s.combinational only fire when the value
    of Signals in their sensitivity list change. This sensitiv

    >>> @s.combinational
    >>> def my_logic()
    >>>   s.out.value = s.in_
    """

    # DEBUG, make permanent to aid debugging?
    #func.func_name = self.name + '.' + func.func_name

    self._combinational_blocks.append( func )
    func._model = self
    return func

  #---------------------------------------------------------------------
  # posedge_clk
  #---------------------------------------------------------------------
  def posedge_clk( self, func ):
    """Decorator to mark register-transfer level sequential logic.

    (This is an alias for @tick_rtl).

    >>> @s.posedge_clk
    >>> def my_logic()
    >>>   s.out.next = s.in_
    """

    self._posedge_clk_blocks.append( func )
    func._model = self
    return func

  #---------------------------------------------------------------------
  # tick
  #---------------------------------------------------------------------
  def tick( self, func ):
    """Decorator to mark a cycle-level sequential logic.

    (This is an alias for @tick_cl).
    """

    self._tick_blocks.append( func )
    func._model = self
    return func

  #-----------------------------------------------------------------------
  # line_trace
  #-----------------------------------------------------------------------
  def line_trace( self ):
    """Returns a one-line string concisely describing Model state for
    the current simulation cycle.

    Model subclasses should implement this method if they would like
    useful debug output when line-tracing is enabled in the simulator.
    """
    return ""

  #---------------------------------------------------------------------
  # elaborate_logic
  #---------------------------------------------------------------------
  def elaborate_logic( self ):
    """DEPRECATED. An abstract method Model subclasses previously
    defined to implement elaboration logic.
    """
    pass

  #=====================================================================
  # Tool API
  #=====================================================================

  #---------------------------------------------------------------------
  # elaborate
  #---------------------------------------------------------------------
  def elaborate( self ):
    """Elaborate a PyMTL model (construct hierarchy, name modules, etc).

    The elaborate() function **must** be called on any instantiated
    top-level model before it is passed to any PyMTL tools.
    """

    # Initialize data structure to hold all model classes in the design
    self._model_classes = set()

    # Recursively elaborate each model in the design, starting with top
    self._recurse_elaborate( self, 'top' )

    # Visit all connections in the design, set directionality
    self._recurse_connections()

  #-----------------------------------------------------------------------
  # is_elaborated
  #-----------------------------------------------------------------------
  def is_elaborated( self):
    """Returns 'True' is elaborate() has been called on this Model."""

    return hasattr( self, 'class_name' )

  #---------------------------------------------------------------------
  # Getters
  #---------------------------------------------------------------------

  def get_inports( self ):
    """Get a list of all InPorts defined by this model."""
    return self._inports

  def get_outports( self ):
    """Get a list of all OutPorts defined by this model."""
    return self._outports

  def get_ports( self, preserve_hierarchy=False ):
    """Get a list of all InPorts and OutPorts defined by this model.

    By default this list is a flattened list of all InPort and OutPort
    objects, including those within PortBundles and PortLists. To return
    a list which preserves this hierarchy, use preserve_hierarchy=True.
    """
    if not preserve_hierarchy:
      return self._inports + self._outports
    else:
      return self._hports

  def get_wires( self ):
    """Get a list of all Wires defined in this model."""
    return self._wires

  def get_submodules( self ):
    """Get a list of all child Models instaniated in this model."""
    return self._submodules

  def get_connections( self ):
    """Get a list of all structural connections made in this model."""
    return self._connections

  def get_tick_blocks( self ):
    """Get a list of all sequential (@tick_*) blocks defined in this
    model."""
    return self._tick_blocks

  def get_posedge_clk_blocks( self ):
    """Get a list of all sequential (@tick_rtl) blocks defined in this
    model."""
    return self._posedge_clk_blocks

  def get_combinational_blocks( self ):
    """Get a list of all combinational (@combinational) blocks defined
    in this model."""
    return self._combinational_blocks

  #=====================================================================
  # Internal Methods
  #=====================================================================

  #---------------------------------------------------------------------
  # _recurse_elaborate
  #---------------------------------------------------------------------
  def _recurse_elaborate( self, current_model, instance_name ):
    """Use reflection to set model attributes and elaborate
    submodels."""

    if current_model.is_elaborated():
      raise Exception("Model {} has already been elaborated!"
                      .format( current_model.class_name ) )

    # Add the target model to the set of all models
    self._model_classes.add( current_model )

    # Set Public Attributes
    current_model.class_name = self._gen_class_name( current_model )
    current_model.parent     = None
    current_model.name       = instance_name

    # DEPRECATED: Call user implemented elaborate_logic() function
    current_model.elaborate_logic()

    # Initialize lists for signals, submodules and connections
    current_model._wires          = []
    current_model._inports        = []
    current_model._outports       = []
    current_model._hports         = []
    current_model._submodules     = []

    # Disable line tracing by default
    current_model._line_trace_en  = False

    if not hasattr( current_model, '_newsenses' ):
      current_model._newsenses   = collections.defaultdict( list )

    # Inspect all user defined model attributes (signals, signal lists,
    # submodels, etc). Set their names, parents, and add them to the
    # appropriate private attribute lists.
    # TODO: do all ports first?
    for name, obj in current_model.__dict__.items():
      if not name.startswith( '_' ):
        self._check_type( current_model, name, obj )
    if hasattr( current_model, '_auto_connects' ):
      current_model._auto_connect()


  #---------------------------------------------------------------------
  # _check_type
  #---------------------------------------------------------------------
  def _check_type( self, current_model, name, obj, nested=False ):
    """Specialize elaboration actions based on object type."""

    if   isinstance( obj, Wire ):
      obj.name              = name
      obj.parent            = current_model
      current_model._wires += [ obj ]

    elif isinstance( obj, InPort ):
      obj.name                = name
      obj.parent              = current_model
      current_model._inports += [ obj ]
      if not nested:
        current_model._hports  += [ obj ]

    elif isinstance( obj, OutPort ):
      obj.name                 = name
      obj.parent               = current_model
      current_model._outports += [ obj ]
      if not nested:
        current_model._hports  += [ obj ]

    # TODO: clean this up...
    elif isinstance( obj, PortBundle ):
      obj.name = name
      for port in obj.get_ports():
        self._check_type(current_model, name+'.'+port.name, port, nested=True)
      if not nested:
        current_model._hports += [ obj ]

    # Submodules
    elif isinstance( obj, Model ):
      # TODO: remove, throw an exception in _recurse_elaborate
      if obj.is_elaborated():
        warnings.warn( "Model '{}::{}' has two parents!!!"
                        .format( obj.__class__.__name__, name ) )
        return

      # Recursively call elaborate() on the submodule
      self._recurse_elaborate( obj, name )
      # Set attributes
      obj.parent                 = current_model
      current_model._submodules += [ obj ]
      # Structurally connect the clk and reset signals
      obj.parent.connect( obj.clk,   obj.parent.clk   )
      obj.parent.connect( obj.reset, obj.parent.reset )

    # Lists of Signals
    elif isinstance( obj, list ):
      if obj and isinstance( obj[0], Wire):
        obj = WireList( obj )
        obj.name = name
        assert '.' not in name
        setattr( current_model, name, obj )
      if obj and isinstance( obj[0], (InPort,OutPort, PortBundle)):
        temp = PortList( obj )
        temp._ports = obj
        obj = temp
        obj.name = name
        assert '.' not in name
        setattr( current_model, name, obj )
        if not nested:
          current_model._hports += [ obj ]
      # Iterate through each item in the list and recursively call the
      # _check_type() utility function
      for i, item in enumerate(obj):
        item_name = "%s[%d]" % (name, i)
        self._check_type( current_model, item_name, item, nested=True )

  #---------------------------------------------------------------------
  # _gen_class_name
  #---------------------------------------------------------------------
  def _gen_class_name( self, model ):
    """Generate a unique class name for model instances."""

    # Base name is always just the class name
    name = model.__class__.__name__

    # TODO: huge hack, fix this!
    for key, value in model._args.items():
      if isinstance( value, Bits.Bits ):
        #print('\nWARNING: assuming Bits parameter wants .nbits, not .value')
        model._args[ key ] = value.nbits

    # Generate a unique name for the Model instance based on its params
    # http://stackoverflow.com/a/5884123
    try:
      hashables = { x for x in model._args.items()
                    if isinstance( x[1], collections.Hashable ) }

      # Also add class name to prevent same-name same-args collisions
      hashables.add( model.__class__ )

      hashables = frozenset( hashables )
      suffix = abs( hash( hashables ) )
      return name + '_' + hex( suffix )
    # No _args attribute, so no need to create a specialized name
    except AttributeError:
      return name

  #---------------------------------------------------------------------
  # _recurse_connections
  #---------------------------------------------------------------------
  # Set the directionality on all connections in the design of a Model.
  def _recurse_connections(self):
    """Set the directionality on all connections in the model."""

    # Set direction of all connections
    for c in self._connections:
      c.set_edge_direction()

    # Recursively enter submodules
    for submodule in self._submodules:
      submodule._recurse_connections()

  #---------------------------------------------------------------------
  # _connect_signal
  #---------------------------------------------------------------------
  def _connect_signal( self, left_port, right_port ):
    """Connect a single pair of Signal objects."""

    # Can't connect a port to itself!
    assert left_port != right_port
    # Create the connection
    connection_edge = ConnectionEdge( left_port, right_port )

    # Add the connection to the Model's connection list
    if not connection_edge:
      raise Exception( "Invalid Connection!")
    self._connections.add( connection_edge )

  #-----------------------------------------------------------------------
  # _connect_bundle
  #-----------------------------------------------------------------------
  def _connect_bundle( self, left_bundle, right_bundle ):
    """Connect all Signal object pairs in a PortBundle."""

    # Can't connect a port to itself!
    assert left_bundle != right_bundle

    ports = zip( left_bundle.get_ports(), right_bundle.get_ports() )

    for left, right in ports:
      self._connect_signal( left, right )

  #-----------------------------------------------------------------------
  # _auto_connect
  #-----------------------------------------------------------------------
  def _auto_connect(self):
    """Connect all InPorts and OutPorts in the parent and one or more
    child modules based on the port name."""

    def port_dict( lst ):
      dictionary = {}
      for port in lst:
        if not port.name == 'clk' and not port.name == 'reset':
          dictionary[port.name] = port
      return dictionary

    for m1,m2 in self._auto_connects:

      dict1 = port_dict( self.get_inports()+self.get_outports() )
      dict2 = port_dict( m1.get_ports() )
      dict3 = port_dict( m2.get_ports() if m2 is not None else [] )

      for key in dict1:
        if key in dict2:
          self.connect(dict1[key],dict2[key])
          del dict2[key]
        if key in dict3:
          self.connect(dict1[key],dict3[key])
          del dict3[key]

      for key in dict3:
        if key in dict2:
          self.connect(dict2[key], dict3[key])

