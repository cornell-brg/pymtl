#=========================================================================
# ast_typer.py
#=========================================================================
# Create a simplified representation of the Python AST for help with
# source to source translation.

import ast, _ast
import re

#-------------------------------------------------------------------------
# TypeAST
#-------------------------------------------------------------------------
class TypeAST( ast.NodeTransformer ):

  def __init__( self, model, func ):
    self.model       = model
    self.func        = func
    self.closed_vars = get_closure_dict( func )



  def visit_Module( self, node ):
    # visit children
    self.generic_visit( node )
    # copy the function body, delete module references
    return ast.copy_location( node.body[0], node )

  def visit_FunctionDef( self, node ):
    # visit children
    self.generic_visit( node )

    # simplified decorator list
    decorator_list = [ x._name for x in node.decorator_list
                       if isinstance( x, Self ) ]

    # create a new FunctionDef node
    new_node = ast.FunctionDef( name=node.name, args=node.args,
                                body=node.body,
                                decorator_list=decorator_list
                               )

    # create a new function that deletes the decorators
    return new_node

  #def visit_Attribute( self, node ):
  #  reverse_branch = ReorderAST(self.self_name).reverse( node )
  #  return ast.copy_location( reverse_branch, node )

  #def visit_Subscript( self, node ):
  #  reverse_branch = ReorderAST(self.self_name).reverse( node )
  #  return ast.copy_location( reverse_branch, node )

  def visit_Name( self, node ):
    # If the name is not in closed_vars, it is a local temporary
    if   node.id not in self.closed_vars:
      new_node = Temp( id=node.id )
    # If the name points to the model, this is a reference to self (or s)
    elif self.closed_vars[ node.id ] is self.model:
      new_node = Self( id=node.id )
    # Otherwise, we have some other variable captured by the closure...
    # TODO: should we allow this?
    else:
      new_node = node

    # Return the new_node
    return ast.copy_location( new_node, node )

  def visit_Index( self, node ):
    # Remove Index nodes, they seem pointless
    child = self.visit( node.value )
    return child

#------------------------------------------------------------------------
# get_closure_dict
#------------------------------------------------------------------------
def get_closure_dict( fn ):
  closure_objects = [c.cell_contents for c in fn.func_closure]
  return dict( zip( fn.func_code.co_freevars, closure_objects ))

#------------------------------------------------------------------------
# ArraySlice
#------------------------------------------------------------------------
class ArraySlice( _ast.Subscript ):
  pass

#------------------------------------------------------------------------
# BitSlice
#------------------------------------------------------------------------
class BitSlice( _ast.Subscript ):
  pass

#------------------------------------------------------------------------
# Self
#------------------------------------------------------------------------
# New AST Node for references to self. Based on Name node.
class Self( _ast.Name ):
  pass

#------------------------------------------------------------------------
# Temp
#------------------------------------------------------------------------
# New AST Node for local temporaries. Based on Name node.
class Temp( _ast.Name ):
  pass

