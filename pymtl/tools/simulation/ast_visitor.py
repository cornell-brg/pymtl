#=========================================================================
# ast_visitor.py
#=========================================================================
# Collection of python ast visitors.  Eventually want:
#
# * Sensitivity List Visitor: detect signals read in @combinational
#   blocks (SimulationTool)
#
# * Variable Name Visitor: converts a small AST branch into it's
#   Python variable name (SimulationTool & VerilogTranslTool)
#
# * Reg Visitor: detect signals written in @combinational and @posedge_clk
#   blocks to determine which signals are 'reg' type (VerilogTranslTool)
#
# * Translation Visitor: translate code in @combinational and @posedge_clk
#   blocks into Verilog syntax.

import ast, _ast

from pymtl import PyMTLError

#------------------------------------------------------------------------
# DetectValueNext
#------------------------------------------------------------------------
class DetectValueNext( ast.NodeVisitor ):

  def __init__( self, func, attr='next or value' ):
    self.attr = attr
    self.func = func

  def visit_Attribute( self, node ):
    if isinstance( node.ctx, _ast.Store ):
      if node.attr == self.attr:
        import inspect
        src,funclineno = inspect.getsourcelines( self.func )
        lineno         = funclineno + node.lineno - 1
        raise PyMTLError(
          'Cannot write .{attr} in a {kind} block!\n\n'
          ' {lineno} {srccode}\n'
          ' File: {filename}\n'
          ' Function: {funcname}\n'
          ' Line: {lineno}\n'.format(
            attr     = self.attr,
            kind     = {'value':'@tick','next':'@combinational'}[ self.attr ],
            srccode  = src[node.lineno-1],
            filename = inspect.getfile( self.func ),
            funcname = self.func.func_name,
            lineno   = lineno,
          )
        )

#------------------------------------------------------------------------
# DetectLoadsAndStores
#------------------------------------------------------------------------
# AST traversal class which detects loads and stores within a concurrent
# block.  Load detection is useful for generating the sensitivity list
# for @combinational blocks in the Simulator.  Store detection is useful
# for determining 'reg' type variables during Verilog translation.
class DetectLoadsAndStores( ast.NodeVisitor ):

  def __init__( self ):
    self.assign = False
    self.load   = [ ]
    self.store  = [ ]

  def enter( self, node ):
    self.visit( node )
    return self.load, self.store

  # Start here, visit each assignment statement and detect:
  # 1) sensitivity list: all variables read
  # 2) reg types: all variables written to
  def visit_Assign( self, node ):
    # We currently don't handle multiple LHS targets
    assert len( node.targets ) == 1

    self.assign = True
    self.visit( node.targets[0] )
    self.visit( node.value )
    self.assign = False

  # Sometimes we encounter an if statement first, this requires us to
  # visit: the test expression, the body of the if statement, and
  # any elif/else blocks at the same indentation level.
  def visit_If( self, node ):
    # Handle the test as if it's an assign, special case.
    self.assign = True
    self.visit( node.test )
    self.assign = False
    # Visit the body and any orelse blocks.
    self.generic_visit( node )

  def visit_Attribute( self, node ):
    if not self.assign: return
    if   isinstance( node.ctx, _ast.Load ):
      self.load  += [ GetVariableName( self ).visit( node ) ]
    elif isinstance( node.ctx, _ast.Store ):
      self.store += [ GetVariableName( self ).visit( node ) ]
    else:
      print( type( node.ctx ) )
      raise Exception( "Unsupported concurrent block code!" )

  def visit_Name( self, node ):
    if not self.assign: return
    if   isinstance( node.ctx, _ast.Load ):
      self.load  += [ GetVariableName( self ).visit( node ) ]
    elif isinstance( node.ctx, _ast.Store ):
      self.store += [ GetVariableName( self ).visit( node ) ]
    else:
      print( type( node.ctx ) )
      raise Exception( "Unsupported concurrent block code!" )

  def visit_Subscript( self, node ):
    if not self.assign: return
    if   isinstance( node.ctx, _ast.Load ):
      self.load  += [ GetVariableName( self ).visit( node ) ]
    elif isinstance( node.ctx, _ast.Store ):
      self.store += [ GetVariableName( self ).visit( node ) ]
    else:
      print( type( node.ctx ) )
      raise Exception( "Unsupported concurrent block code!" )

  # TODO: need this to detect writes to bit slices?
  #def visit_Subscript( self, node ):
  #  if not self.assign: return
  #  if   isinstance( node.ctx, _ast.Load ):
  #    self.load  += [ GetVariableName( self ).visit( node ) ]
  #  elif isinstance( node.ctx, _ast.Store ):
  #    self.store += [ GetVariableName( self ).visit( node ) ]
  #  else:
  #    print( type( node.ctx ) )
  #    raise Exception( "Unsupported concurrent block code!" )


#------------------------------------------------------------------------
# GetVariableName
#------------------------------------------------------------------------
# Converts an AST branch, beginning with the indicated node, into it's
# corresponding Python name.  Meant to be called as a utility visitor
# by another AST visitor, which should pass a reference to itself as
# a parameter.
class GetVariableName( ast.NodeVisitor ):

  def __init__( self, parent ):
    self.parent = parent

  def visit_Attribute( self, node ):
    return self.visit( node.value ) + '.' + node.attr

  def visit_Subscript( self, node ):
    self.parent.visit( node.slice )
    # insert eval here to test for type...
    return self.visit( node.value ) + '[?]'

  def visit_Name( self, node ):
    return node.id

