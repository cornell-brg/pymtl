#=========================================================================
# Model.py
#=========================================================================
# Base modeling components for constructing hardware description models.
#
# This module contains a collection of classes that can be used to
# construct MTL (pronounced metal) models. Once constructed, a MTL model
# can be leveraged by a number of tools for various purposes (simulation,
# translation into HDLs, etc).

from ConnectionEdge import ConnectionEdge
from signals        import Signal, InPort, OutPort, Wire, Constant
#from physical      import PhysicalDimensions

#import PortBundle
import collections
import inspect

#-------------------------------------------------------------------------
# Model
#-------------------------------------------------------------------------
# User visible base class for hardware models.
#
# Provides utility classes for elaborating connectivity between components,
# giving instantiated subcomponents proper names, and building datastructures
# that can be leveraged by various MTL tools.
#
# Any user implemented model that wishes to make use of the various MTL tools
# should subclass this.
#
class Model(object):

  #-----------------------------------------------------------------------
  # elaborate
  #-----------------------------------------------------------------------
  # Elaborate a MTL model (construct hierarchy, name modules, etc.).
  #
  # The elaborate() function must be called on an instantiated toplevel
  # module before it is passed to any MTL tools!
  def elaborate(self):

    # Initialize data structure to hold all model classes in the design
    self.model_classes = set()

    # Recursively elaborate each model in the design, starting with top
    self.recurse_elaborate( self, 'top' )

    # Recursively visit all connections in the design, set directionality
    self.recurse_connections()

  #-----------------------------------------------------------------------
  # elaborate_logic (Abstract)
  #-----------------------------------------------------------------------
  # Abstract method, must be implemented by subclasses!
  # TODO: use abc module to create abstract method?
  def elaborate_logic( self ):
    raise NotImplementedError( "Model '{}' needs to implement the "
                               "'elaborate_logic()' method!"
                               "".format( self.class_name ) )

  #-----------------------------------------------------------------------
  # recurse_elaborate
  #-----------------------------------------------------------------------
  # Utility method to perform elaboration on a Model and it's submodules.
  def recurse_elaborate( self, current_model, instance_name ):

    # Add the target model to the set of all models
    self.model_classes.add( current_model )

    # Set Public Attributes
    current_model.class_name = self.gen_class_name( current_model )
    current_model.parent     = None
    current_model.name       = instance_name

    # Setup default InPorts
    current_model.clk        = InPort(1)
    current_model.reset      = InPort(1)

    # Initialize function lists for concurrent blocks
    current_model._tick_blocks          = []
    current_model._posedge_clk_blocks   = []
    current_model._combinational_blocks = []

    # Call user implemented elaborate_logic() function
    current_model.elaborate_logic()

    # Initialize lists for signals, submodules and connections
    current_model._wires          = []
    current_model._inports        = []
    current_model._outports       = []
    current_model._submodules     = []
    if not hasattr( current_model, '_connections' ):
      current_model._connections = set()

    # Disable line tracing by default
    current_model._line_trace_en  = False

    if not hasattr( current_model, '_newsenses' ):
      current_model._newsenses   = collections.defaultdict( list )

    # Verilog translation specific variables
    current_model._localparams = set()
    current_model._tempwires   = {}
    current_model._temparrays  = []
    current_model._tempregs    = []
    current_model._loopvars    = []

    # Inspect all user defined model attributes (signals, signal lists,
    # submodels, etc). Set their names, parents, and add them to the
    # appropriate private attribute lists.
    # TODO: do all ports first?
    for name, obj in current_model.__dict__.items():
      if not name.startswith( '_' ):
        self.check_type( current_model, name, obj )

  #-----------------------------------------------------------------------
  # check_type
  #-----------------------------------------------------------------------
  # Utility method to specialize elaboration actions based on object type.
  def check_type( self, current_model, name, obj ):

    # Wires
    if   isinstance( obj, Wire ):
      obj.name              = name
      obj.parent            = current_model
      current_model._wires += [ obj ]

    # InPorts
    elif isinstance( obj, InPort ):
      obj.name                = name
      obj.parent              = current_model
      current_model._inports += [ obj ]

    # OutPorts
    elif isinstance( obj, OutPort ):
      obj.name                 = name
      obj.parent               = current_model
      current_model._outports += [ obj ]

    ## PortBundles
    #elif isinstance( obj, PortBundle.PortBundle ):
    #  for port_name, obj in obj.__dict__.items():
    #    self.check_type(current_model, name+'_M_'+port_name, obj)

    # Submodules
    elif isinstance( obj, Model ):
      # Recursively call elaborate() on the submodule
      self.recurse_elaborate( obj, name )
      # Set attributes
      obj.parent                 = current_model
      current_model._submodules += [ obj ]
      # Structurally connect the clk and reset signals
      obj.parent.connect( obj.clk,   obj.parent.clk   )
      obj.parent.connect( obj.reset, obj.parent.reset )

    # Local Parameters (int)
    elif isinstance( obj, int ):
      # TODO: add support for floats?
      current_model._localparams.add( (name, obj) )

    # Lists of Signals
    elif isinstance( obj, list ):
      # TODO: hacky signal check, implement using SignalList instead?
      if obj and isinstance( obj[0], Signal ):
        current_model._temparrays.append( name )
      # Iterate through each item in the list and recursively call the
      # check_type() utility function
      for i, item in enumerate(obj):
        item_name = "%s[%d]" % (name, i)
        self.check_type( current_model, item_name, item )

  #-----------------------------------------------------------------------
  # gen_class_name
  #-----------------------------------------------------------------------
  # Generate a unique class name for model instances.
  def gen_class_name( self, model ):

    # Base name is always just the class name
    name = model.__class__.__name__

    # If the @capture_args decorator has been used, generate a unique
    # name for the Model instance based on its parameters
    try:
      for arg_name, arg_val in model._args.items():
        name += "_{}_{}".format( arg_name, arg_val )
      return name
    # No _args attribute, so no need to create a specialized name
    except AttributeError:
      return name

  #-----------------------------------------------------------------------
  # recurse_connections
  #-----------------------------------------------------------------------
  # Set the directionality on all connections in the design of a Model.
  def recurse_connections(self):

    # Set direction of all connections
    for c in self._connections:
      self.set_edge_direction( c )

    # Recursively enter submodules
    for submodule in self._submodules:
      submodule.recurse_connections()

  #-----------------------------------------------------------------------
  # set_edge_direction
  #-----------------------------------------------------------------------
  # Set the edge direction of a single ConnectionEdge.
  def set_edge_direction(self, edge):

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

  #-----------------------------------------------------------------------
  # __setattr__
  #-----------------------------------------------------------------------

  #def __setattr__( self, name, value ):
  #  if name in self.__dict__ and isinstance( self.__dict__[ name ], Bits):
  #    self.__dict__[ name ].uint = value
  #  else:
  #    self.__dict__[ name ] = value

  #-----------------------------------------------------------------------
  # Getters
  #-----------------------------------------------------------------------

  def get_inports( self ):
    return self._inports

  def get_outports( self ):
    return self._outports

  def get_ports( self ):
    return self._inports + self._outports

  def get_wires( self ):
    return self._wires

  def get_submodules( self ):
    return self._submodules

  def get_localparams( self ):
    return self._localparams

  def get_connections( self ):
    return self._connections

  #-----------------------------------------------------------------------
  # Decorators
  #-----------------------------------------------------------------------
  # TODO: add documentation!

  def tick( self, func ):
    self._tick_blocks.append( func )
    return func

  def combinational( self, func ):
    # DEBUG, make permanent to aid debugging?
    #func.func_name = self.name + '.' + func.func_name
    self._combinational_blocks.append( func )
    return func

  def posedge_clk( self, func ):
    self._posedge_clk_blocks.append( func )
    return func

  #-----------------------------------------------------------------------
  # connect
  #-----------------------------------------------------------------------
  def connect( self, left_port, right_port ):

    # Can't connect a port to itself!
    assert left_port != right_port

    # Create the connection
    connection_edge = ConnectionEdge( left_port, right_port)

    # Add the connection to the Model's connection list
    # TODO: this is hacky, FIX
    if not hasattr( self, '_connections' ):
      self._connections = set()
    if not connection_edge: raise Exception( "Invalid Connection!")
    self._connections.add( connection_edge )

  #-----------------------------------------------------------------------
  # connect_dict
  #-----------------------------------------------------------------------
  def connect_dict( self, connections ):
   for left_port, right_port in connections.iteritems():
     self.connect( left_port, right_port )

  #def connect( left, right=None ):
  # if type(left) == dict:
  #   connect_dict( left )
  # else:
  #   connect_ports( left, right )

  #-----------------------------------------------------------------------
  # register_combinational
  #-----------------------------------------------------------------------
  # Explicitly register functions callbacks to the signals provided
  # in sensitivity_list.
  # TODO: Add this back in later?
  #def register_combinational( self, func_name, sensitivity_list ):
  #  self._newsenses = collections.defaultdict( list )
  #  self._newsenses[ func_name ] = sensitivity_list

  #-----------------------------------------------------------------------
  # dump_physical_design
  #-----------------------------------------------------------------------
  # Print out the physical design.
  # TODO: Add this back in later?
  #def dump_physical_design( self, prefix='' ):
  #  pass

  #-----------------------------------------------------------------------
  # is_elaborated
  #-----------------------------------------------------------------------
  # Returns 'True' is elaborate() has been called on the Model.
  def is_elaborated( self):
    return hasattr( self, 'class_name' )

  #-----------------------------------------------------------------------
  # line_trace
  #-----------------------------------------------------------------------
  # Having a default line trace makes it easier to just always enable
  # line tracing in the test harness. -cbatten
  def line_trace( self ):
    return ""

#------------------------------------------------------------------------
# Decorators
#------------------------------------------------------------------------

import inspect
# Returns a traced version of the input function.
# TODO: add to decorators section above
def capture_args(fn):

  #@functools.wraps(fn)
  def wrapped(*v, **k):

    # get the names of the functions arguments
    argspec = inspect.getargspec( fn )

    # the self pointer is always the first positional arg
    self = v[0]

    # create an argument dictionary
    args = collections.OrderedDict()
    # add all the positional arguments
    for i in range(1, len(v)):
      if isinstance( v[i], int ):
        value = v[i]
      else:
        #raise Exception("Untranslatable param type!")
        # WARNING: taking abs() of hash, increases chance of collision?
        value = hex( abs( hash( v[i] )) )
      key = argspec.args[ i ]
      args[ key ] = value
    # then add all the named arguments
    for key, val in k.items():
      if isinstance( val, int ):
        value = val
      else:
        # WARNING: taking abs() of hash, increases chance of collision?
        value = hex( abs( hash( val )) )
      args[key] = value

    # add the arguments and their values to the object so it can be
    # used during static elaboration to create the name
    self._args = args

    return_val  = fn(*v, **k)
    return return_val

  return wrapped


