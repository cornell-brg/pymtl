#=========================================================================
# Simulation Tool
#=========================================================================
# Tool for simulating MTL models.
#
# This module contains classes which construct a simulator given a MTL model
# for execution in the python interpreter.

import pprint

from new_Bits import Bits

#=========================================================================
# SimulationTool
#=========================================================================
# User visible class implementing a tool for simulating MTL models.
#
# This class takes a MTL model instance and creates a simulator for execution
# in the python interpreter.
class SimulationTool():

  #-----------------------------------------------------------------------
  # Constructor
  #-----------------------------------------------------------------------
  # Construct a simulator from a MTL model.
  def __init__(self, model):

    # Check that the model has been elaborated
    if not model.is_elaborated():
      msg  = "cannot initialize {0} tool.\n".format(self.__class__.__name__)
      msg += "Provided model has not been elaborated yet!!!"
      raise Exception(msg)

    self.model      = model
    self.value_sets = []

    # Actually construct the simulator
    self.construct_sim()

  #-----------------------------------------------------------------------
  # Construct Simulator
  #-----------------------------------------------------------------------
  # Construct a simulator for the provided model.
  def construct_sim(self):
    self.group_connection_nodes( self.model )
    self.insert_value_nodes()

  #-----------------------------------------------------------------------
  # Find Node Groupings
  #-----------------------------------------------------------------------
  def group_connection_nodes( self, model ):

    # DEBUG
    #print 70*'-'
    #print "Model:", model
    #print "Ports:"
    #pprint.pprint( model.get_ports(), indent=3 )
    #print "Submodules:"
    #pprint.pprint( model.get_submodules(), indent=3 )

    #def a_printer( some_set ):
    #  return [ x.parent.name + '.' + x.name for x in some_set ]
    #t = [ a_printer( [ x.src_node, x.dest_node] ) for x in model.get_connections() ]
    #print "Connections:"
    #pprint.pprint( model.get_connections(), indent=3 )
    #pprint.pprint( t, indent=3 )

    for m in model.get_submodules():
      self.group_connection_nodes( m )

    # Create value nodes starting at the leaves, should simplify
    # ConnectionGraph minimization?
    for c in model.get_connections():

      # Temporary exception
      if c.src_slice or c.dest_slice:
        raise Exception( "Slices not supported yet!" )

      # Create a new value set containing this connections ports
      new_group = set( [ c.src_node, c.dest_node ] )
      updated = True

      # See if this value set has overlap with another set, if
      # so, return the union of that group and see if the union
      # has overlap with other sets.   Otherwise add the new grouping
      # to the collection of value sets.
      while updated:
        updated = False
        for group in self.value_sets:
          if not group.isdisjoint( new_group ):
            new_group = group.union( new_group )
            self.value_sets.remove( group )
            updated = True
            break
        if not updated:
          self.value_sets.append( new_group )

  #-----------------------------------------------------------------------
  # Replace Ports with Value Nodes
  #-----------------------------------------------------------------------
  def insert_value_nodes( self ):

    # DEBUG
    print
    print "NODE SETS"
    for set in self.value_sets:
      print '    ', [ x.parent.name + '.' + x.name for x in set ]

    # Each grouping is a bits object, make all ports pointing to
    # it point to the Bits object instead
    for group in self.value_sets:
      temp  = group.pop()
      value = Bits( temp.nbits )
      group.add( temp )
      for x in group:
        if 'IDX' in x.name:
          name, idx = x.name.split('IDX')
          x.parent.__dict__[ name ][ int (idx) ] = value
        else:
          x.parent.__dict__[ x.name ] = value

