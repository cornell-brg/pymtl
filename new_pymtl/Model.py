#=======================================================================
# Model.py
#=======================================================================
# Base modeling components for constructing hardware description models.
#
# This module contains a collection of classes that can be used to
# construct MTL (pronounced metal) models. Once constructed, a MTL model
# can be leveraged by a number of tools for various purposes
# (simulation, translation into HDLs, etc).

from metaclasses    import MetaCollectArgs
from ConnectionEdge import ConnectionEdge
from signals        import Signal, InPort, OutPort, Wire, Constant
from signal_lists   import PortList, WireList
from PortBundle     import PortBundle

#from physical      import PhysicalDimensions

import collections
import inspect
import warnings
import math

from greenlet import greenlet

#=======================================================================
# Model
#=======================================================================
# User visible base class for hardware models.
#
# Provides utility classes for elaborating connectivity between
# components, giving instantiated subcomponents proper names, and
# building datastructures that can be leveraged by various tools.
#
# Any user implemented model that wishes to make use of the various
# tools should subclass this.
#
class Model( object ):

  __metaclass__ = MetaCollectArgs

  #=====================================================================
  # Modeling API
  #=====================================================================

  #---------------------------------------------------------------------
  # elaborate_logic (Abstract)
  #---------------------------------------------------------------------
  # Abstract method, must be implemented by subclasses!
  # TODO: use abc module to create abstract method?
  def elaborate_logic( self ):
    raise NotImplementedError( "Model '{}' needs to implement the "
                               "'elaborate_logic()' method!"
                               "".format( self.class_name ) )

  #-----------------------------------------------------------------------
  # line_trace
  #-----------------------------------------------------------------------
  # Having a default line trace makes it easier to just always enable
  # line tracing in the test harness. -cbatten
  def line_trace( self ):
    return ""

  def __call__(self):
    self._tick_blocks          = []
    self._posedge_clk_blocks   = []
    self._model._combinational_blocks = []

    super( MetaCollectArgs, self ).__call__( *args, **kwargs )

  #---------------------------------------------------------------------
  # Decorators
  #---------------------------------------------------------------------
  # TODO: add documentation!

  def tick( self, func ):
    try:
      self._tick_blocks.append( func )
    except: 
      self._tick_blocks = [func]
    func._model = self
    return func

  def combinational( self, func ):
    # DEBUG, make permanent to aid debugging?
    #func.func_name = self.name + '.' + func.func_name
    try:
      self._combinational_blocks.append( func )
    except:
      self._combinational_blocks = [func]
    func._model = self
    return func

  def posedge_clk( self, func ):
    try:
      self._posedge_clk_blocks.append( func )
    except:
      self._posedge_clk_blocks = [func]
    func._model = self
    return func

  #---------------------------------------------------------------------
  # pausable_tick
  #---------------------------------------------------------------------
  # Experimental support for creating tick blocks where we can pause the
  # execution within the tick block. This avoids the need for creating a
  # GreenletWrapper explicitly.

  def pausable_tick( self, func ):

    # The inner_wrapper function is the one which we will wrap in a
    # greenlet. It calls the tick function forever. It pauses after each
    # call to the tick function, but the tick function itself can also
    # pause.

    def inner_wrapper():
      while True:

        # Call the tick function

        func()

        # Yield so we always only do one tick per cycle

        greenlet.getcurrent().parent.switch(0)

    # Create a greenlet and save it with the model. Note that we
    # currently only allow a single pausable_tick per model.

    self._pausable_tick = greenlet(inner_wrapper)

    # The outer_wrapper is what will become the new tick function. This
    # is what gets added to the tick list.

    def outer_wrapper():
      self._pausable_tick.switch()

    try:
      self._tick_blocks.append( outer_wrapper )
    except:
      self._tick_blocks = [ outer_wrapper ]

    outer_wrapper._model = self
    return outer_wrapper

  #---------------------------------------------------------------------
  # connect
  #---------------------------------------------------------------------
  def connect( self, left_port, right_port ):

    if  isinstance( left_port, PortBundle ):
      self._connect_bundle( left_port, right_port )
    else:
      self._connect_signal( left_port, right_port )

    # elif isinstance( left_port, dict ):
    #   self.connect_dict( left_port )

  #-----------------------------------------------------------------------
  # connect_dict
  #-----------------------------------------------------------------------
  def connect_dict( self, connections ):

   for left_port, right_port in connections.iteritems():
     self.connect( left_port, right_port )

  #=====================================================================
  # Tool API
  #=====================================================================

  #---------------------------------------------------------------------
  # elaborate
  #---------------------------------------------------------------------
  # Elaborate a MTL model (construct hierarchy, name modules, etc.).
  #
  # The elaborate() function must be called on an instantiated toplevel
  # module before it is passed to any MTL tools!
  def elaborate( self ):

    # Initialize data structure to hold all model classes in the design
    self._model_classes = set()

    # Recursively elaborate each model in the design, starting with top
    self._recurse_elaborate( self, 'top' )

    # Visit all connections in the design, set directionality
    self._recurse_connections()

  #-----------------------------------------------------------------------
  # is_elaborated
  #-----------------------------------------------------------------------
  # Returns 'True' is elaborate() has been called on the Model.
  def is_elaborated( self):
    return hasattr( self, 'class_name' )

  #---------------------------------------------------------------------
  # Getters
  #---------------------------------------------------------------------

  def get_inports( self ):
    return self._inports

  def get_outports( self ):
    return self._outports

  def get_ports( self, preserve_hierarchy=False ):
    if not preserve_hierarchy:
      return self._inports + self._outports
    else:
      return self._hports

  def get_wires( self ):
    return self._wires

  def get_submodules( self ):
    return self._submodules

  def get_connections( self ):
    return self._connections

  def get_tick_blocks( self ):
    return self._tick_blocks

  def get_posedge_clk_blocks( self ):
    return self._posedge_clk_blocks

  def get_combinational_blocks( self ):
    return self._combinational_blocks

  #=====================================================================
  # Internal Methods
  #=====================================================================

  #---------------------------------------------------------------------
  # _recurse_elaborate
  #---------------------------------------------------------------------
  # Use reflection to set model attributes and elaborate submodels.
  def _recurse_elaborate( self, current_model, instance_name ):

    if current_model.is_elaborated():
      raise Exception("Model {} has already been elaborated!"
                      .format( current_model.class_name ) )

    # Add the target model to the set of all models
    self._model_classes.add( current_model )

    # Set Public Attributes
    current_model.class_name = self._gen_class_name( current_model )
    current_model.parent     = None
    current_model.name       = instance_name

    # Setup default InPorts
    current_model.clk        = InPort(1)
    current_model.reset      = InPort(1)

    # Initialize function lists for concurrent blocks
    try:
      current_model._tick_blocks[0]
    except:
      current_model._tick_blocks          = []
    try:
      current_model._posedge_clk_blocks[0]
    except:
      current_model._posedge_clk_blocks   = []
    try:
      current_model._combinational_blocks[0]
    except:
      current_model._combinational_blocks = []

    # Call user implemented elaborate_logic() function
    current_model.elaborate_logic()

    # Initialize lists for signals, submodules and connections
    current_model._wires          = []
    current_model._inports        = []
    current_model._outports       = []
    current_model._hports         = []
    current_model._submodules     = []
    if not hasattr( current_model, '_connections' ):
      current_model._connections = set()

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
  # Specialize elaboration actions based on object type.
  def _check_type( self, current_model, name, obj, nested=False ):

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
  # Generate a unique class name for model instances.
  def _gen_class_name( self, model ):

    # Base name is always just the class name
    name = model.__class__.__name__

    # Generate a unique name for the Model instance based on its params
    # http://stackoverflow.com/a/5884123
    try:
      hashables = frozenset({ x for x in model._args.items()
                              if isinstance( x[1], collections.Hashable ) })
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
    # Set direction of all connections
    for c in self._connections:
      self._set_edge_direction( c )

    # Recursively enter submodules
    for submodule in self._submodules:
      submodule._recurse_connections()

  #---------------------------------------------------------------------
  # _set_edge_direction
  #---------------------------------------------------------------------
  # Set the edge direction of a single ConnectionEdge.
  def _set_edge_direction(self, edge):

    a = edge.src_node
    b = edge.dest_node

    # Constants should always be the source node
    if isinstance( a, Constant ): return
    if isinstance( b, Constant ): edge.swap_direction()

    # Model connecting own InPort to own OutPort
    elif ( a.parent == b.parent and
           isinstance( a, OutPort ) and isinstance( b, InPort  )):
      edge.swap_direction()

    # Model InPort connected to InPort of a submodule
    elif ( a.parent in b.parent._submodules and
           isinstance( a, InPort  ) and isinstance( b, InPort  )):
      edge.swap_direction()

    # Model OutPort connected to OutPort of a submodule
    elif ( b.parent in a.parent._submodules and
           isinstance( a, OutPort ) and isinstance( b, OutPort )):
      edge.swap_direction()

    # Model OutPort connected to InPort of a submodule
    elif ( a.parent in b.parent._submodules and
           isinstance( a, InPort ) and isinstance( b, OutPort )):
      edge.swap_direction()

    # Wire connected to InPort
    elif ( a.parent == b.parent and
           isinstance( a, Wire ) and isinstance( b, InPort )):
      edge.swap_direction()

    # Wire connected to OutPort
    elif ( a.parent == b.parent and
           isinstance( a, OutPort ) and isinstance( b, Wire )):
      edge.swap_direction()

    # Wire connected to InPort of a submodule
    elif ( a.parent in b.parent._submodules and
           isinstance( a, InPort  ) and isinstance( b, Wire )):
      edge.swap_direction()

    # Wire connected to OutPort of a submodule
    elif ( b.parent in a.parent._submodules and
           isinstance( a, Wire ) and isinstance( b, OutPort )):
      edge.swap_direction()

    # Chaining submodules together (OutPort of one to InPort of another)
    elif ( a.parent != b.parent and a.parent.parent == b.parent.parent and
           isinstance( a, InPort  ) and isinstance( b, OutPort )):
      edge.swap_direction()

  #---------------------------------------------------------------------
  # _connect_signal
  #---------------------------------------------------------------------
  # Connect a single pair of Signal objects.
  def _connect_signal( self, left_port, right_port ):
    # Can't connect a port to itself!
    assert left_port != right_port
    # Create the connection
    connection_edge = ConnectionEdge( left_port, right_port )

    # Add the connection to the Model's connection list
    # TODO: this is hacky, FIX
    if not hasattr( self, '_connections' ):
      self._connections = set()
    if not connection_edge: raise Exception( "Invalid Connection!")
    self._connections.add( connection_edge )

  #-----------------------------------------------------------------------
  # _connect_bundle
  #-----------------------------------------------------------------------
  # Connect all Signal object pairs in a PortBundle.
  def _connect_bundle( self, left_bundle, right_bundle ):

    # Can't connect a port to itself!
    assert left_bundle != right_bundle

    ports = zip( left_bundle.get_ports(), right_bundle.get_ports() )

    for left, right in ports:
      self._connect_signal( left, right )

  def _port_dict( self, lst ):

    dictionary = {}
    for port in lst:
      if not port.name == 'clk' and not port.name == 'reset':
        dictionary[port.name] = port
    return dictionary

  def _auto_help( self, p1, p2, p3, m2, m3):

    dict1 = self._port_dict(p1)
    dict2 = self._port_dict(p2)
    dict3 = self._port_dict(p3)

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

  def _auto_connect(self):
    for m1,m2 in self._auto_connects:
      ports1 = m1.get_ports()
      ports2 = m2.get_ports() if m2 is not None else []
      self._auto_help(self._inports+self._outports, ports1, ports2, m1, m2)

  def connect_auto( self, m1, m2 = None ):
    if not hasattr( self, '_auto_connects' ):
      self._auto_connects = []
    self._auto_connects.append((m1,m2))





