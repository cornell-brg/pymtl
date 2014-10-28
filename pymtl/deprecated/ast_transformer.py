#=========================================================================
# ast_tranformer.py
#=========================================================================
# Create a simplified representation of the Python AST for help with
# source to source translation.

import ast, _ast
import re

#-------------------------------------------------------------------------
# SimplifiedAST
#-------------------------------------------------------------------------
class SimplifiedAST( ast.NodeTransformer ):

  def __init__( self, self_name=None ):
    self.self_name   = self_name

  def visit_Module( self, node ):
    # visit children
    self.generic_visit( node )
    # copy the function body, delete module references
    return ast.copy_location( node.body[0], node )

  def visit_FunctionDef( self, node ):
    # store self_name
    # TODO: fix so that this properly detects the "self" param
    if node.args.args: s = node.args.args[0].id
    else:              s = 's'
    self.self_name   = s
    # visit children
    self.generic_visit( node )
    # simplified decorator list
    decorator_list = [ x._name for x in node.decorator_list
                       if isinstance( x, Self ) ]
    # create a new FunctionDef node
    new_node = ast.FunctionDef( name=node.name, args=node.args,
                                body=node.body,
                                decorator_list=decorator_list
                                #decorator_list=[]
                               )
    # create a new function that deletes the decorators
    return new_node

  #def visit_Attribute( self, node ):
  #  reverse_branch = ReorderAST(self.self_name).reverse( node )
  #  return ast.copy_location( reverse_branch, node )
  #def visit_Subscript( self, node ):
  #  reverse_branch = ReorderAST(self.self_name).reverse( node )
  #  return ast.copy_location( reverse_branch, node )
  #def visit_Index( self, node ):
  #  reverse_branch = ReorderAST(self.self_name).reverse( node )
  #  return ast.copy_location( reverse_branch, node )

  def visit_Name( self, node ):
    new_node = LocalVar( id=node.id )
    new_node._name = node.id
    return ast.copy_location( new_node, node )


#-------------------------------------------------------------------------
# ReorderAST
#-------------------------------------------------------------------------
# Reorders an AST branch beginning with the indicated node.  Intended
# for inverting the order of Name/Attribute chains so that the Name
# node comes first, followed by chains of Attribute/Subscript nodes.
#
# This visitor will also insert Self nodes to represent references to the
# self variable, and remove Index nodes which seem to serve no useful
# purpose.

class ReorderAST( ast.NodeVisitor ):

  def __init__( self, self_name ):
    self.self_name = self_name
    self.stack     = []

  def reverse( self, tree ):
    # Visit the tree
    self.visit( tree )

    # The top of the stack is the new root of the tree
    current = new_root = self.stack.pop()
    name    = [current._name]

    # Pop each node off the stack, update pointers
    while self.stack:
      next_         = self.stack.pop()
      current.value = next_
      current       = next_
      name.append( current._name )

    # Name generation
    new_root._name = '.'.join( name ).replace('.[', '[')

    # Update the last pointer to None, return the new_root
    current.value = None
    return new_root

  def visit_Name( self, node ):
    # TODO: Make sure name is actually self before transforming.
    if node.id == self.self_name:
      n = Self( attr=node.id )
    else:
      n = LocalObject( attr=node.id )
    # Name generation
    n._name = node.id
    self.stack.append( n )

  def visit_Attribute( self, node ):
    # Name generation
    node._name = node.attr
    self.stack.append( node )
    self.visit( node.value )

  def visit_Subscript( self, node ):
    node.slice = SimplifiedAST( self.self_name ).visit( node.slice)
    self.stack.append( node )
    # Name generation
    #node._name = '[{}]'.format( node.slice._name )
    node._name = '[?]'
    self.visit( node.value )

  def visit_Index( self, node ):
    # Index nodes are dumb.  Remove them by not adding them to the stack.
    self.visit( node.value )

  def visit_Slice( self, node ):
    assert node.step == None
    self.stack.append( node )
    node.lower = SimplifiedAST( self.self_name ).visit( node.lower )
    node.upper = SimplifiedAST( self.self_name ).visit( node.upper )
    # Name generation
    #node._name = "{}:{}".format( node.lower._name, node.upper._name )
    node._name = "?:?"

  def visit_Num( self, node ):
    # Name generation
    node._name = str( node.n )
    self.stack.append( node )

#------------------------------------------------------------------------
# Self
#------------------------------------------------------------------------
# New AST Node for references to self. Based on Attribute node.
class Self( _ast.Attribute ):
  value = None

#------------------------------------------------------------------------
# LocalVar
#------------------------------------------------------------------------
# New AST Node for local vars. Based on Name node.
class LocalVar( _ast.Name ):
  pass

#------------------------------------------------------------------------
# LocalObj
#------------------------------------------------------------------------
# New AST Node for local vars. Based on Name node.
class LocalObject( _ast.Attribute ):
  pass

