#=========================================================================
# ast_tools.py
#=========================================================================

import ast, _ast
import re

from ..ast_helpers import get_closure_dict

#-------------------------------------------------------------------------
# AnnotateWithObjects
#-------------------------------------------------------------------------
# Annotates AST Nodes with the live Python objects they reference.
class AnnotateWithObjects( ast.NodeTransformer ):

  def __init__( self, model, func ):
    self.model       = model
    self.func        = func
    self.closed_vars = get_closure_dict( func )
    self.current_obj = None

  def visit_Attribute( self, node ):
    self.generic_visit( node )

    # TODO: handle self.current_obj == None.  These are temporary
    #       locals that we should check to ensure their types don't
    #       change!

    if self.current_obj:
      try :
        x = self.current_obj.getattr( node.attr )
        self.current_obj.update( node.attr, x )
      except AttributeError:
        if node.attr not in ['next', 'value', 'n', 'v']:
          raise Exception("Error: Unknown attribute for this object: {}"
                          .format( node.attr ) )

    node._object = self.current_obj.inst if self.current_obj else None

    return node

  def visit_Name( self, node ):

    # If the name is not in closed_vars, it is a local temporary
    if   node.id not in self.closed_vars:
      new_obj  = None

    # If the name points to the model, this is a reference to self (or s)
    elif self.closed_vars[ node.id ] is self.model:
      new_obj  = PyObj( '', self.closed_vars[ node.id ] )

    # Otherwise, we have some other variable captured by the closure...
    # TODO: should we allow this?
    else:
      new_node = node
      new_obj  = PyObj( node.id, self.closed_vars[ node.id ] )

    # Store the new_obj
    self.current_obj = new_obj
    node._object = self.current_obj.inst if self.current_obj else None

    # Return the new_node
    return node

#-------------------------------------------------------------------------
# RemoveValueNext
#-------------------------------------------------------------------------
# Remove .value and .next.
class RemoveValueNext( ast.NodeTransformer ):

  def visit_Attribute( self, node ):

    if node.attr in ['next', 'value', 'n', 'v']:
      # Update the Load/Store information
      node.value.ctx = node.ctx
      return ast.copy_location( node.value, node )

    return node

#-------------------------------------------------------------------------
# RemoveSelf
#-------------------------------------------------------------------------
# Remove references to self.
# TODO: make Attribute attached to self a Name node?
class RemoveSelf( ast.NodeTransformer ):

  def __init__( self, model ):
    self.model       = model

  def visit_Name( self, node ):
    if node._object == self.model:
      return None
    return node

#-------------------------------------------------------------------------
# RemoveModule
#-------------------------------------------------------------------------
# Remove the module node.
class RemoveModule( ast.NodeTransformer ):

  def visit_Module( self, node ):
    #self.generic_visit( node ) # visit children, uneeded?

    # copy the function body, delete module references
    return ast.copy_location( node.body[0], node )

#-------------------------------------------------------------------------
# SimplifyDecorator
#-------------------------------------------------------------------------
# Make the decorator contain text strings, not AST Trees
class SimplifyDecorator( ast.NodeTransformer ):

  def visit_FunctionDef( self, node ):
    #self.generic_visit( node ) # visit children, uneeded?

    # TODO: currently only support one decorator
    # TODO: currently assume decorator is of the form 'self.dec_name'
    assert len( node.decorator_list )
    dec = node.decorator_list[0].attr

    # create a new FunctionDef node that deletes the decorators
    new_node = ast.FunctionDef( name=node.name, args=node.args,
                                body=node.body, decorator_list=[dec])

    return ast.copy_location( new_node, node )

#-------------------------------------------------------------------------
# ThreeExprLoops
#-------------------------------------------------------------------------
# Replace calls to range()/xrange() in a for loop with a Slice object
# describing the bounds (upper/lower/step) of the iteration.
class ThreeExprLoops( ast.NodeTransformer ):

  def visit_For( self, node ):

    assert isinstance( node.iter,      _ast.Call ) # TODO: allow iterables
    assert isinstance( node.iter.func, _ast.Name )
    call = node.iter
    assert call.func.id in ['range','xrange']

    if   len( call.args ) == 1:
      start = _ast.Num( n=0 )
      stop  = call.args[0]
      step  = _ast.Num( n=1 )
    elif len( call.args ) == 2:
      start = call.args[0]
      stop  = call.args[1]
      step  = _ast.Num( n=1 ) # TODO: should be an expression
    elif len( call.args ) == 3:
      start = call.args[0]
      stop  = call.args[1]
      step  = call.args[2]
    else:
      raise Exception("Invalid # of arguments to range function!")

    node.iter = _ast.Slice( lower=start, upper=stop, step=step )

    return node

#-------------------------------------------------------------------------
# GetRegsTempsArrays
#-------------------------------------------------------------------------
# Make the decorator contain text strings, not AST Trees
class GetRegsTempsArrays( ast.NodeVisitor ):

  def get( self, tree ):
    self.store  = set()
    self.visit( tree )
    return self.store

  def visit_Assign( self, node ):
    assert len(node.targets) == 1
    self.store.add( node.targets[0]._object )

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
  def __repr__( self ):
    return "PyObj( name={} inst={} )".format( self.name, type(self.inst) )
