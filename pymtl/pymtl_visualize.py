import pygraphviz as pgv
from pymtl_model import *
from pymtl_simulate import *
import pymtl_debug


class GraphvizDiagram(object):
  """User visible class for translating MTL models into Verilog source."""

  def __init__(self, model):
    """Construct a Verilog translator from a MTL model.

    Parameters
    ----------
    model: an instantiated MTL model (Model).
    """
    self.model = model
    self.g     = pgv.AGraph(directed=True,rankdir='LR')
    #self.g.graph_attr['rankdir'] = 'LR'
    #self.g.node_attr['fixedsize']='true'
    #self.g.node_attr['shape']    = 'circle'

  def generate(self, target=None, graph=None):

    # This allows us to make this function recursive
    if not target:
      target = self.model
    if not graph:
      graph = self.g

    # Utility function to generate the name module_name.port_name
    def get_port_name(port):
      return "{0}.{1}".format( port.parent.name, port.name )

    # Add all of this modules ports to the graph, also assign them to the
    # correct subgraph
    port_names = [ get_port_name(x) for x in target._ports ]
    # TODO: isn't coloring all ports correctly...
    graph.add_nodes_from( port_names, style = 'filled' )
    subg = graph.add_subgraph( nbunch = port_names, label = target.name,
                               name = "cluster_"+target.name)

    # Iterate through all the ports and add directional arrows
    for port in target._ports:
      p_name = get_port_name(port)
      # Get at the value node, special case for slices
      node = port._value
      if isinstance(port._value, Slice):
        node = port._value._value
      # Add value nodes if they exist
      if node is not None:
        node_name = id(node)
        node_label = "node {0:5}bits".format( node.width )
        graph.add_node( node_name, label=node_label, color='gray' )
        graph.add_edge(p_name, node_name, color='gray')
      # Add all connections
      for connect in port.connections:
        c_name = get_port_name(connect)
        # Add slices to the correct subwhatever
        if isinstance(connect, Slice) and connect.parent.name == target.name:
          subg.add_node( get_port_name(connect) )
        # Bugfix: port coloring issue
        elif isinstance(connect, Port):
          graph.add_node(c_name, style = 'filled' )

        # Assign a direction to the edge.
        # port is InPort   and connection is internal: port -> connection
        #                  and connection is external: connection -> port
        # port is OutPort: and connection is external: connection -> port
        #                  and connection is internal: port -> connection
        if   isinstance(port, InPort)  and connect in port.int_connections:
          graph.add_edge(p_name, c_name, label=connect.width, fontsize=8)
        elif isinstance(port, InPort)  and connect in port.ext_connections:
          graph.add_edge(c_name, p_name, label=connect.width, fontsize=8)
        elif isinstance(port, OutPort) and connect in port.int_connections:
          graph.add_edge(c_name, p_name, label=connect.width, fontsize=8)
        elif isinstance(port, OutPort) and connect in port.ext_connections:
          graph.add_edge(p_name, c_name, label=connect.width, fontsize=8)
        else:
          print "WTFFFFF"
          assert False

    # Iterate through all the submodules and call generate recursively
    for m in target._submodules:
      self.generate( m, subg )

    # TODO: show logic blocks
    #for sync in target._posedge_clks:
    #for sync in target._combinationals:
      #subg = graph.add_subgraph()


  def to_diagram(self, filename):
    # layout types: neato dot twopi circo fdp nop
    self.g.layout(prog='dot')
    self.g.draw(filename)

  def to_text(self):
    print self.g.string()

def dump_ast():
  print
  print
  import inspect
  import ast
  model_class = model.__class__
  src = inspect.getsource( model_class )
  tree = ast.parse( src )
  pymtl_debug.print_ast( tree )


if __name__ == '__main__':

  from pymtl_test_examples import *
  model_list = [
    Rotator(8),
    #RotatorSlice(8), # DNE!
    SimpleSplitter(4),
    SimpleMerger(4),
    ComplexSplitter(16,2),
    ComplexMerger(16,4),
    OneWire(32),
    OneWireWrapped(8),
    Register(4),
    RegisterWrapper(4),
    RegisterChain(4),
    RegisterSplitter(4),
    FullAdder(),
    # TODO: fix filling on some of the ports...
    RippleCarryAdder(4),
    Incrementer(),
    Counter(),
    # Good examples
    CountIncr(),
    RegIncr(),
    IncrReg(),
    GCD(),
  ]

  for model in model_list:
    model.elaborate()
    cname = model.class_name
    print "* Visualizing " + cname
    plot = GraphvizDiagram(model)
    plot.generate()
    plot.to_diagram('_{0}.png'.format(cname))

    sim = LogicSim(model)
    sim.generate()
    plot.generate()
    plot.to_diagram('_{0}_vnode.png'.format(cname))

    # Debugging
    #pymtl_debug.port_walk( model )
    #plot.to_text()

