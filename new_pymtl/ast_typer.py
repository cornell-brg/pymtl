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
    self.current_obj = None

  #-----------------------------------------------------------------------
  # visit_Module
  #-----------------------------------------------------------------------
  def visit_Module( self, node ):
    # visit children
    self.generic_visit( node )
    # copy the function body, delete module references
    return ast.copy_location( node.body[0], node )

  #-----------------------------------------------------------------------
  # visit_FunctionDef
  #-----------------------------------------------------------------------
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

  #-----------------------------------------------------------------------
  # visit_Attribute
  #-----------------------------------------------------------------------
  def visit_Attribute( self, node ):
    self.visit( node.value )

    # TODO: handle self.current_obj == None.  These are temporary
    #       locals that we should check to ensure their types don't
    #       change!

    if self.current_obj:
      x = self.current_obj.getattr( node.attr )
      self.current_obj.update( node.attr, x )

    return node

  #-----------------------------------------------------------------------
  # visit_Name
  #-----------------------------------------------------------------------
  def visit_Name( self, node ):

    # If the name is not in closed_vars, it is a local temporary
    if   node.id not in self.closed_vars:
      new_node = Temp( id=node.id )
      new_obj  = None

    # If the name points to the model, this is a reference to self (or s)
    elif self.closed_vars[ node.id ] is self.model:
      new_node = Self( id=node.id )
      new_obj  = PyObj( '', self.closed_vars[ node.id ] )

    # Otherwise, we have some other variable captured by the closure...
    # TODO: should we allow this?
    else:
      new_node = node
      new_obj  = PyObj( node.id, self.closed_vars[ node.id ] )

    # Store the new_obj
    self.current_obj = new_obj

    # Return the new_node
    return ast.copy_location( new_node, node )

  #-----------------------------------------------------------------------
  # visit_Subscript
  #-----------------------------------------------------------------------
  #def visit_Subscript( self, node ):
  #  return node

  #-----------------------------------------------------------------------
  # visit_Index
  #-----------------------------------------------------------------------
  def visit_Index( self, node ):
    # Remove Index nodes, they seem pointless
    child = self.visit( node.value )
    return child

#------------------------------------------------------------------------
# PyObj
#------------------------------------------------------------------------
class PyObj( object ):
  def __init__( self, name, inst ):
    self.name  = name
    self.inst  = inst
  def update( self, name, inst ):
    self.name += name
    self.inst  = inst
  def getattr( self, name ):
    return getattr( self.inst, name )


#------------------------------------------------------------------------
# get_closure_dict
#------------------------------------------------------------------------
# http://stackoverflow.com/a/19416942
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

