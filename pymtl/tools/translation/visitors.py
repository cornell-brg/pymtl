#=========================================================================
# visitors.py
#=========================================================================

from __future__ import print_function

import ast, _ast
import re
import warnings

from ..ast_helpers         import get_closure_dict, print_simple_ast
from ...model.signals      import Wire, Signal, InPort, OutPort, _SignalSlice
from ...model.Model        import Model
from ...model.PortBundle   import PortBundle
from ...model.signal_lists import PortList, WireList
from ...datatypes.Bits     import Bits
from exceptions            import VerilogTranslationError

#-------------------------------------------------------------------------
# AnnotateWithObjects
#-------------------------------------------------------------------------
# Annotates AST Nodes with the live Python objects they reference.
# TODO: store objects in PyObj wrapper, or not?
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
          raise Exception('Unknown attribute "{}" in model "{}"'
                          .format( node.attr, self.model.__class__ ))

    node._object = self.current_obj.inst if self.current_obj else None

    return node

  def visit_Name( self, node ):

    # Check if the name is a global constant
    if   node.id in self.func.func_globals:
      new_obj  = PyObj( '', self.func.func_globals[ node.id ] )

    # If the name is not in closed_vars or func_globals, it's a local temporary
    elif node.id not in self.closed_vars:
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

  def visit_Subscript( self, node ):

    # Visit the object being sliced
    new_value = self.visit( node.value )

    # Visit the index of the slice; stash and restore the current_obj
    stash, self.current_obj = self.current_obj, None
    new_slice = self.visit( node.slice )
    self.current_obj = stash

    # Update the current_obj
    # TODO: check that type of all elements in item are identical
    # TODO: won't work for lists that are initially empty
    # TODO: what about lists that initially contain None?
    # TODO: do we want the array, or do we want element 0 of the array...
    node._object = self.current_obj.inst if self.current_obj else None
    if self.current_obj:
      self.current_obj.update( '[]', self.current_obj.inst[0] )

    return node

  def visit_List( self, node ):

    node._object = []
    for item in node.elts:
      self.visit( item )
      node._object.append( item._object )

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
# FlattenSubmodAttrs
#-------------------------------------------------------------------------
# Transform AST branches for submodule signals. A PyMTL signal referenced
# as 's.submodule.port' would appear in the AST as:
#
#   Attribute(port)
#   |- Attribute(submodule)
#
# This visitor transforms the AST and name to 's.submodule_port':
#
#   Attribute(submodule$port)
#
class FlattenSubmodAttrs( ast.NodeTransformer ):

  def __init__( self ):
    self.submodule = None

  def visit_Attribute( self, node ):

    # Visit children
    self.generic_visit( node )

    # If the direct child of this attribute was a submodule then the node
    # will be removed by the visitor. We must update our name to include
    # submodule name for proper mangling.
    if self.submodule:
      new_node = _ast.Name( id  = '{}${}'.format(self.submodule, node.attr ),
                            ctx = node.ctx )
      new_node._object = node._object
      node = new_node

    # Attribute is a submodel remove the node, set the submodule name
    if hasattr( node._object, 'class_name' ):
      self.submodule = node._object.name
      return None

    # Otherwise, clear the submodule name, return node unmodified
    self.submodule = None
    return ast.copy_location( node, node )

#-------------------------------------------------------------------------
# FlattenPortBundles
#-------------------------------------------------------------------------
# Transform AST branches for PortBundle signals. A PyMTL signal referenced
# as 's.portbundle.port' would appear in the AST as:
#
#   Attribute(port)
#   |- Attribute(portbundle)
#
# This visitor transforms the AST and name to 's.submodule_port':
#
#   Attribute(portbundle_port)
#
class FlattenPortBundles( ast.NodeTransformer ):

  def __init__( self ):
    self.portbundle = None

  def visit_Attribute( self, node ):

    # Visit children
    self.generic_visit( node )

    # If the direct child of this attribute was a portbundle then the node
    # will be removed by the visitor. We must update our name to include
    # portbundle name for proper mangling.
    if self.portbundle:
      new_node = _ast.Name( id  = '{}_{}'.format(self.portbundle, node.attr ),
                            ctx = node.ctx )
      new_node._object = node._object
      node = new_node

    # Attribute is a PortBundle, remove the node, set the submodule name
    if isinstance( node._object, PortBundle ):
      self.portbundle = node.attr
      return None

    # Otherwise, clear the submodule name, return node unmodified
    self.portbundle = None
    return ast.copy_location( node, node )

  def visit_Name( self, node ):

    # Name is a PortBundle, remove the node, set the submodule name
    if isinstance( node._object, PortBundle ):
      self.portbundle = node.id
      return None

    # Otherwise, clear the submodule name, return node unmodified
    self.portbundle = None
    return node

#-------------------------------------------------------------------------
# FlattenListAttrs
#-------------------------------------------------------------------------
# Transform AST branches for attribute accesses from indexed objects.
# Attributes referenced as 's.sig[i].attr' would appear in the AST as:
#
#   Attribute(attr)
#   |- Subscript()
#      |- Attribute(sig)
#      |- Index()
#         |- Name(i)
#
# This visitor transforms the AST and name to 's.sig_attr[i]':
#
#   Subscript()
#   |- Attribute(sig_attr)
#   |- Index()
#      |- Name(i)
#
class FlattenListAttrs( ast.NodeTransformer ):

  def __init__( self ):
    self.attr = None

  def visit_Attribute( self, node ):

    # If a parent node is going to be removed, update this name

    # SubModel List
    if self.attr   and isinstance( node._object[0], Model ):
      node.attr = '{}${}'.format( node.attr, self.attr )
      node._object = PortList([ getattr( x, self.attr ) for x in node._object ])
      node._object.name = node.attr

    # PortBundle List
    elif self.attr and isinstance( node._object[0], PortBundle ):
      node.attr = '{}_{}'.format( node.attr, self.attr )
      node._object = PortList([ getattr( x, self.attr ) for x in node._object ])
      node._object.name = node.attr

    # Unknown!!!
    elif self.attr:
      raise Exception( "Don't know how to flatten this!" )

    # Exit early if theres no value attribute
    if not hasattr( node, 'value' ):
      return node

    # If the child is a subscript node, this node will be removed
    if isinstance( node.value, ast.Subscript ):
      self.attr = node.attr
      self.generic_visit( node )
      self.attr = None
      node = node.value

    return ast.copy_location( node, node )

  def visit_Subscript( self, node ):

    # Update the _object in Subscript too!
    if self.attr:
      if   isinstance( node._object[0], Model ):
        name = '{}${}'.format( node._object[0].name.split('[')[0], self.attr )
        node._object = PortList([ getattr( x, self.attr ) for x in node._object ])
        node._object.name = name
      elif isinstance( node._object[0], PortBundle ):
        if   isinstance( node.value, ast.Name ):
          bundle_name = node.value.id
        elif isinstance( node.value, ast.Attribute ):
          bundle_name = node.value.attr
        else:
          raise Exception()
        name = '{}_{}'.format( bundle_name, self.attr )
        node._object = PortList([ getattr( x, self.attr ) for x in node._object ])
        node._object.name = name
      else:
        return node

    # Visit the slice
    stash = self.attr
    self.attr = None
    node.slice = self.visit( node.slice )
    self.attr = stash

    # Visit the value
    node.value = self.visit( node.value )

    return node

  def visit_Name( self, node ):

    # SubModel List
    if self.attr   and isinstance( node._object[0], Model ):
      node.id = '{}${}'.format( node.id, self.attr )
      node._object = PortList([ getattr( x, self.attr ) for x in node._object ])
      node._object.name = node.id

    # PortBundle List
    elif self.attr and isinstance( node._object[0], PortBundle ):
      node.id = '{}_{}'.format( node.id, self.attr )
      node._object = PortList([ getattr( x, self.attr ) for x in node._object ])
      node._object.name = node.id

    # Unknown!!!
    elif self.attr:
      raise Exception( "Don't know how to flatten this!" )

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

    # TODO: currently assume decorator is of the form 'self.dec_name'
    if len( node.decorator_list ) != 1:
      def get_dec_name( dec ):
        if   hasattr( dec, 'id'   ): return dec.id
        elif hasattr( dec, 'attr' ): return dec.attr
        else:                        return dec
      raise VerilogTranslationError(
        'Translated behavioral blocks should only have one decorator!\n'
        'Current decorators: {}'.format(
          [ get_dec_name( x ) for x in node.decorator_list ]
        ), node.lineno
      )

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
    self.generic_visit( node )

    if not ( isinstance( node.iter,      _ast.Call ) and
             isinstance( node.iter.func, _ast.Name ) and
             node.iter.func.id in ['range', 'xrange'] ):
      raise VerilogTranslationError(
        'For loops are only translatable when using range or xrange!\n'
        'Please use "for i in range(...)/xrange(...)".',
        node.lineno
      )

    call = node.iter

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
# ConstantToSlice
#-------------------------------------------------------------------------
class ConstantToSlice( ast.NodeTransformer ):

  def visit_Attribute( self, node ):
    self.generic_visit( node )
    if isinstance( node._object, slice ):
      assert not node._object.step
      new_node = ast.Slice( ast.Num( node._object.start ),
                            ast.Num( node._object.stop ),
                            None )
      return ast.copy_location( new_node, node )
    return node

  def visit_Name( self, node ):
    self.generic_visit( node )
    if isinstance( node._object, slice ):
      assert not node._object.step
      new_node = ast.Slice( ast.Num( node._object.start ),
                            ast.Num( node._object.stop ),
                            None )
      return ast.copy_location( new_node, node )
    return node

#-------------------------------------------------------------------------
# BitStructToSlice
#-------------------------------------------------------------------------
class BitStructToSlice( ast.NodeTransformer ):

  def visit_Attribute( self, node ):
    self.generic_visit( node )
    if isinstance( node._object, _SignalSlice ):
      assert not node._object.slice.step
      new_node = ast.Subscript( node.value,
                   ast.Slice( ast.Num( node._object.slice.start ),
                              ast.Num( node._object.slice.stop ),
                              None ),
                   None,
                 )
      new_node._object = node._object
      return ast.copy_location( new_node, node )
    return node

#-------------------------------------------------------------------------
# InferTemporaryTypes
#-------------------------------------------------------------------------
import copy
class InferTemporaryTypes( ast.NodeTransformer ):
  last_model = None
  func_id    = 0

  def __init__( self, model ):
    self.model      = model
    self.infer_dict = {}

    # Create unique ids for each function we visit in a given model.
    # This ensures we can assign unique names to temporaries to provide
    # 'scoping' behavior similar to Python.
    if id(self.model) != InferTemporaryTypes.last_model:
      InferTemporaryTypes.last_model = id(self.model)
      InferTemporaryTypes.func_id    = 0
    else:
      InferTemporaryTypes.func_id   += 1

  def _insert( self, node, value ):
    node.targets[0]._object = value
    self.infer_dict[ node.targets[0].id ] = value

  def _uniq_name( self, node_id ):
    return node_id + '__{}'.format( self.func_id )

  def visit_Assign( self, node ):

    # First visit the RHS to update Name nodes that have been inferred
    self.visit( node.value )

    # Catch untranslatable constructs
    if len(node.targets) != 1:
      raise VerilogTranslationError(
        'Chained assignments are not supported!\n'
        'Please modify "x = y = ..." to be two separate lines.',
        node.lineno
      )

    if isinstance(node.targets[0], (ast.Tuple)):
      raise VerilogTranslationError(
        'Multiple items on the left of an assignment are not supported!\n'
        'Please modify "x,y = ..." to be two separate lines.',
        node.lineno
      )

    # Need this to visit potential temporaries used in slice indices!
    self.visit( node.targets[0] )

    # The LHS doesn't have a type, we need to infer it
    if node.targets[0]._object == None:

      # The LHS should be a Name node!
      assert isinstance(node.targets[0], _ast.Name)

      # Assign unique name to this temporary in case the same temporary
      # name is used in another concurrent block.
      node.targets[0].id = self._uniq_name( node.targets[0].id )

      # Copy the object returned by the RHS, set the name appropriately
      if   isinstance( node.value, ast.Name ):
        if isinstance( node.value._object, int ):
          self._insert( node, (node.targets[0].id, node.value._object ) )
        else:
          obj = copy.copy( node.value._object )
          obj.name   = node.targets[0].id
          obj.parent = None
          self._insert( node, obj )

      elif isinstance( node.value, ast.Attribute ):
        if isinstance( node.value._object, int ):
          self._insert( node, (node.targets[0].id, node.value._object ) )
        else:
          obj = copy.copy( node.value._object )
          obj.name   = node.targets[0].id
          obj.parent = None
          self._insert( node, obj )

      elif isinstance( node.value, ast.Num ):
        self._insert( node, (node.targets[0].id, int( node.value.n )) )

      elif isinstance( node.value, ast.BoolOp ):
        obj      = Wire( 1 )
        obj.name = node.targets[0].id
        self._insert( node, obj )

      elif isinstance( node.value, ast.Compare ):
        obj      = Wire( 1 )
        obj.name = node.targets[0].id
        self._insert( node, obj )

      # TODO: assumes ast.Index does NOT contain a slice object
      elif isinstance( node.value,       ast.Subscript ) and \
           isinstance( node.value.slice, ast.Index     ):

        if isinstance( node.value.slice.value, ast.Slice ):
          signal_name = node.targets[0].id
          model_name  = self.model.__class__
          raise Exception('Cannot infer "{}" in model "{}": '
                          'RHS slice wider than a single bit!'
                          .format( signal_name, model_name ) )

        obj      = Wire( 1 )
        obj.name = node.targets[0].id
        self._insert( node, obj )

      elif isinstance( node.value, ast.Call ):

        func_name = node.value.func.id
        if func_name in ['sext', 'zext']:
          nbits_arg = node.value.args[1]
          if isinstance( nbits_arg, ast.Num ): nbits = nbits_arg.n
          else:                                nbits = nbits_arg._object
          assert isinstance( nbits, int )
          obj      = Wire( nbits )
        elif func_name == 'concat':
          nbits    = sum( [x._object.nbits for x in node.value.args ] )
          obj      = Wire( nbits )
        elif func_name in ['reduce_and', 'reduce_or', 'reduce_xor']:
          obj      = Wire( 1 )
        elif func_name == 'Bits':
          nbits_arg = node.value.args[0]
          if isinstance( nbits_arg, ast.Num ): nbits = nbits_arg.n
          else:                                nbits = nbits_arg._object
          assert isinstance( nbits, int )
          obj      = Wire( nbits )
        else:
          print_simple_ast( node )
          raise Exception('Cannot infer type from Function "{}" in model "{}"!'
                          .format( func_name, self.model.__class__ ) )

        obj.name = node.targets[0].id
        self._insert( node, obj )

      else:
        print_simple_ast( node )
        raise Exception('Cannot infer type from "{}" nodes in model "{}"!'
                        .format( node.value, self.model.__class__ ) )

    return node

  def visit_Name( self, node ):
    try:
      if node._object == None:
        # Update all other references to inferred temporaries to use the
        # newly assigned uniquified name.
        temp_name = self._uniq_name( node.id )
        node._object = self.infer_dict[ temp_name ]
        node.id = temp_name
    except KeyError:
      pass

    return node

#-------------------------------------------------------------------------
# PortListNameHack
#-------------------------------------------------------------------------
# Temporary hack to handle cases where
class PortListNameHack( ast.NodeTransformer ):

  def __init__( self, model ):
    self.model = model

  def visit_Subscript( self, node ):

    self.generic_visit( node )
    plist = node._object

    # skip check if this isn't a PortList or WireList

    if not isinstance( plist, (PortList, WireList) ):
      return node

    # if the PortList parent is not the same as the current modules parent, but
    # there is no '$' in the name, it's been named improperly! fix it!

    if plist[0].parent != self.model and not '$' in plist.name:

      # this only works if all children of the list have the same parent, throw
      # an error if we can detect that that is not the case

      if len( plist) > 1 and plist[0].parent != plist[1].parent:
        raise Exception( "Error during translation!" )

      # generate the updated name, and also make a copy of the PortList to make
      # sure we aren't impacting any other AST references to this object

      name              = '{}${}'.format( plist[0].parent.name, plist.name )
      node._object      = PortList( node._object )
      node._object.name = name

    return node


#-------------------------------------------------------------------------
# GetRegsIntsTempsArrays
#-------------------------------------------------------------------------
# TODO: for loop temporaries (ComplexBitSplit)
class GetRegsIntsParamsTempsArrays( ast.NodeVisitor ):

  def get( self, tree ):

    self._is_lhs   = False
    self.store     = {}
    self.loopvar   = set()
    self.params    = set()
    self.arrays    = set()
    self.arrayelms = set()
    self.visit( tree )
    return set( self.store.values() ), self.loopvar, self.params, self.arrays

  def visit_Attribute( self, node ):
    if isinstance( node._object, (int,Bits) ):
      self.params.add( (node.attr, node._object) )
    #self.generic_visit( node )

  def visit_Name( self, node ):
    if isinstance( node._object, (int,Bits) ):
      self.params.add( (node.id, node._object) )
    #self.generic_visit( node )

  def visit_Assign( self, node ):
    assert len(node.targets) == 1

    self._is_lhs = True
    self.visit( node.targets[0] )
    self._is_lhs = False
    self.visit( node.value )

    obj = node.targets[0]._object

    # NOTE:
    # - currently possible to have inferences with different bitwidths
    # - currently possible for a signal to be stored as both a reg and loopvar
    #   handle this in verilog_structural.create_declarations
    if   obj in self.arrayelms:     return
    elif isinstance( obj, Signal ): self.store[ obj.fullname ] = obj
    elif isinstance( obj, tuple ):  self.loopvar.add( obj[0] )
    # FIXME:
    # - if one field of a bitstruct is assigned in a behavioral block,
    #   the **entire** bitstruct is assumed to be a reg!
    elif isinstance( obj, _SignalSlice ):
      self.store[ obj._signal.fullname ] = obj._signal

  def visit_For( self, node ):
    assert isinstance( node.iter,   _ast.Slice )
    assert isinstance( node.target, _ast.Name  )
    self.loopvar.add( node.target.id )
    self.generic_visit( node )

  def visit_Subscript( self, node ):

    # TODO: Check for PortList/WireList explicitly?
    if isinstance( node._object, list ):

      # Keep track if this array ever appears on the lhs
      # (if so, should be declared reg)
      try:                   node._object.is_lhs |= self._is_lhs
      except AttributeError: node._object.is_lhs  = self._is_lhs

      # Add arrays to our tracking datastructures
      self.arrays   .add   ( node._object )
      self.arrayelms.update( node._object )

    # visit value to find nested subscripts
    self.visit( node.value )

    # visit slice to find params
    self.visit( node.slice )

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

