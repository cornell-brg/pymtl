#=========================================================================
# ast_visitor.py
#=========================================================================
# Collection of python ast visitors.

import ast, _ast
import inspect

from pymtl               import PyMTLError
from pymtl.model.signals import Signal
from ..ast_helpers       import get_closure_dict

#------------------------------------------------------------------------
# DetectIncorectValueNext
#------------------------------------------------------------------------
class DetectIncorrectValueNext( ast.NodeVisitor ):

  def __init__( self, func, attr='next or value' ):
    self.attr = attr
    self.func = func

  def visit_Attribute( self, node ):
    if isinstance( node.ctx, _ast.Store ):
      if node.attr == self.attr:
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
# DetectMissingValueNext
#------------------------------------------------------------------------
class DetectMissingValueNext( ast.NodeVisitor ):

  def __init__( self, func, attr='next or value' ):
    self.attr   = (attr, attr[0])
    self.func   = func
    self.dict_  = get_closure_dict( func )

    self.src, self.funclineno = inspect.getsourcelines( self.func )

  def visit_Assign( self, node ):

    # Because the lhs could contain arbitrary nesting of tuples or lists,
    # flatten these all out to get the target for each assignment.

    def flatten_targets( tgt, lst ):
      if   isinstance( tgt, list ):
        for x in tgt: flatten_targets( x, lst )
      elif isinstance( tgt, (ast.Tuple,ast.List) ):
        for x in tgt.elts: flatten_targets( x, lst )
      elif isinstance( tgt, (ast.Attribute,ast.Name,ast.Subscript) ):
        lst.append( tgt )
      else:
        from ..ast_helpers import print_simple_ast
        print_simple_ast( tgt )
        raise Exception(
          'Unsupported assignment type ({kind})!\n'
          'Please notify the PyMTL developers!\n\n'
          ' {lineno} {srccode}\n'
          ' File: {filename}\n'
          ' Function: {funcname}\n'
          ' Line: {lineno}\n'.format(
            attr     = self.attr[0],
            kind     = tgt.__class__,
            srccode  = self.src[ node.lineno - 1 ],
            filename = inspect.getfile( self.func ),
            funcname = self.func.func_name,
            lineno   = self.funclineno + node.lineno - 1
          )
        )

    targets = []
    flatten_targets( node.targets, targets )

    # For each assignment AST node, get the targets. If targets do not
    # end with .value or .next, verify this is not a Signal object
    # (InPort, OutPort, Wire)
    # FIXME: second item of self.attr tuple is for .n and .v. Rm these?

    for lhs in targets:
      if not isinstance( lhs, ast.Attribute ) or lhs.attr not in self.attr:

        # TODO: this is super hacky. Grab each left-hand side (LHS)
        # target, give them Load() instead of Store() contexts, and wrap
        # them in an ast.Expression node. This allows us to compile the
        # AST as an expression and execute it with eval(), which will
        # return the object stored in the lhs target. The second argument
        # to eval() is closure dictionary we extracted from the function.

        ## DEBUG
        #print inspect.getfile( self.func )
        #print self.funclineno + node.lineno - 1, self.src[ node.lineno - 1 ]
        ## DEBUG

        # In order to handle lists of Signals, we replace all complex
        # Indexes with the value zero. This will return the first element
        # in the list.
        try:
          lhs     = ReplaceIndexesWithZero().visit( lhs )
          lhs.ctx = ast.Load()
          _code   = compile( ast.Expression( lhs ), '<ast>', 'eval' )
          _temp   = eval( _code, self.dict_ )
        except (NameError, AttributeError) as e:
          # We can't really do anything about temporaries created inside
          # the combinational block without performing a real type
          # inference analysis pass.
          _temp = None
        except IndexError as e:
          # Empty list, nothing to do.
          _temp = None

        # if the object stored in LHS is a Signal, raise a PyMTLError
        if isinstance( _temp, Signal ):
          raise PyMTLError(
            'Attempting to write a(n) {kind} without .{attr}!\n\n'
            ' {lineno} {srccode}\n'
            ' File: {filename}\n'
            ' Function: {funcname}\n'
            ' Line: {lineno}\n'.format(
              attr     = self.attr[0],
              kind     = _temp.__class__.__name__,
              srccode  = self.src[ node.lineno - 1 ],
              filename = inspect.getfile( self.func ),
              funcname = self.func.func_name,
              lineno   = self.funclineno + node.lineno - 1
            )
          )

#------------------------------------------------------------------------
# ReplaceIndexesWithZero
#------------------------------------------------------------------------
class ReplaceIndexesWithZero( ast.NodeTransformer ):
  def visit_Index( self, node ):
    return ast.Index(
      ast.copy_location( ast.Num(0), node.value )
    )

#------------------------------------------------------------------------
# DetectDecorators
#------------------------------------------------------------------------
class DetectDecorators( ast.NodeVisitor ):

  def __init__( self ):
    self.decorators = []

  def enter( self, node ):
    self.visit( node )
    return self.decorators

  def visit_FunctionDef( self, node ):
    [ self.visit(x) for x in  node.decorator_list ]

  def visit_Attribute( self, node ):
    self.decorators.append( node.attr )

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

    self.assign = True
    for target in node.targets:
      self.visit( target )
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

