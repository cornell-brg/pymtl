import pygraphviz as pgv
from pymtl_test_examples import *


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

    if not target:
      target = self.model
    if not graph:
      graph = self.g

    def get_port_name(port):
      return "{0}.{1}".format( port.parent.name, port.name )

    # Add all the ports
    port_names = [ get_port_name(x) for x in target._ports ]
    # TODO: isn't coloring all ports correctly...
    graph.add_nodes_from( port_names, style = 'filled' )
    subg = graph.add_subgraph( nbunch = port_names, label = target.name,
                               name = "cluster_"+target.name)

    for port in target._ports:
      p_name = get_port_name(port)
      #node = graph.get_node( p_name )
      #if isinstance(port, InPort):
      #  node.attr['ordering'] = 'in'
      #elif isinstance(port, OutPort):
      #  node.attr['ordering'] = 'out'
      for connect in port.connections:
        c_name = get_port_name(connect)
        # Add slices to the correct subwhatever
        if isinstance(connect, Slice) and connect.parent.name == target.name:
          subg.add_node( get_port_name(connect) )

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

    for m in target._submodules:
      self.generate( m, subg )

    #for sync in target._posedge_clks:
    #for sync in target._combinationals:
      #subg = graph.add_subgraph()


  def to_diagram(self, filename):
    # layout types: neato dot twopi circo fdp nop
    #self.g.layout(prog='dot')
    self.g.layout(prog='dot')
    self.g.draw(filename)

  def to_text(self):
    print self.g.string()

#for port in model._ports:
#  port_name = "{0}.{1}".format( port.parent.name, port.name )
#  g.add_node( port_name )


#model = Rotator(8)
#model = RotatorSlice(8)
#model = SimpleSplitter(4)
#model = SimpleMerger(4)
#model = ComplexSplitter(16,2)
#model = ComplexMerger(16,4)
#model = OneWire(32)
#model = OneWireWrapped(8)
#model = Register(4)
#model = RegisterWrapper(4)
#model = RegisterChain(4)
#model = RegisterSplitter(4)
#model = FullAdder()
# TODO: fix filling on some of the ports...
#model = RippleCarryAdder(4)
#model = Incrementer()
#model = Counter()
model = CountIncr()
#model = RegIncr()
#model = IncrReg()
model.elaborate()
print
print
#import pymtl_debug
#pymtl_debug.port_walk( model )

plot = GraphvizDiagram(model)
plot.generate()
plot.to_diagram('_abc.png')
#plot.to_text()

