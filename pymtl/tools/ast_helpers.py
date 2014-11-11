#=======================================================================
# ast_helpers.py
#=======================================================================

import inspect
import ast, _ast

#-----------------------------------------------------------------------
# print_ast
#-----------------------------------------------------------------------
# Print out Python AST with nice indenting. Borrowed shamelessly from:
# http://alexleone.blogspot.com/2010/01/python-ast-pretty-printer.html
def print_ast(node, annotate_fields=True, include_attributes=False, indent='  '):

  def _format(node, level=0):
    if isinstance(node, ast.AST):
      fields = [(a, _format(b, level)) for a, b in ast.iter_fields(node)]
      if include_attributes and node._attributes:
        fields.extend([(a, _format(getattr(node, a), level))
                       for a in node._attributes])
      return ''.join([
        node.__class__.__name__,
        '(',
        ', '.join(('%s=%s' % field for field in fields)
                   if annotate_fields else
                   (b for a, b in fields)),
        ')'])
    elif isinstance(node, list):
      lines = ['[']
      lines.extend((indent * (level + 2) + _format(x, level + 2) + ','
                   for x in node))
      if len(lines) > 1:
          lines.append(indent * (level + 1) + ']')
      else:
          lines[-1] += ']'
      return '\n'.join(lines)
    return repr(node)

  if not isinstance(node, ast.AST):
    raise TypeError('expected AST, got %r' % node.__class__.__name__)
  print _format(node)

#-----------------------------------------------------------------------
# print_simple_ast
#-----------------------------------------------------------------------
# Print out Python AST with nice indenting. Borrowed (with modification)
# from:
# http://alexleone.blogspot.com/2010/01/python-ast-pretty-printer.html
def print_simple_ast(node, indent=' '):

  def get_indent( level, pipe=True ):
    if level == 0: return ''
    elif pipe:     return '  '*(level-1) + "|-"
    else:          return '  '*(level-1)

  def _format(node, field='', level=0):
    if isinstance(node, ast.AST):

      head_string  = get_indent( level ) + node.__class__.__name__
      head_string += " ({})".format(field) if field else ""
      body_string  = ""
      for label, value in ast.iter_fields(node):
        if label == "ctx":
          continue
        if isinstance( value, (str, int, float, long) ):
          head_string +=  '  {} = {}'.format( label, value )
        elif not value:
          body_string += get_indent( level+1, pipe=True) + '{} ({})\n'.format( value, label )
        else:
          body_string += _format( value, label, level+1 )

      return head_string + "\n" + body_string

    elif isinstance(node, list):
      string = ''
      for x in node:
        string += _format( x, field, level )
      return string

    return repr(node)

  if not isinstance(node, ast.AST):
    raise TypeError('expected AST, got %r' % node.__class__.__name__)
  print _format(node)

#-----------------------------------------------------------------------
# get_method_ast
#-----------------------------------------------------------------------
# In order to parse class methods and inner functions, we need to fix the
# indentation whitespace or else the ast parser throws an "unexpected
# ident" error.
import re
p = re.compile('( *(@|def))')
def get_method_ast( func ):

  src = inspect.getsource( func )
  new_src = p.sub( r'\2', src )
  tree = ast.parse( new_src )
  return tree, new_src

#-----------------------------------------------------------------------
# get_closure_dict
#-----------------------------------------------------------------------
# http://stackoverflow.com/a/19416942
def get_closure_dict( fn ):
  closure_objects = [c.cell_contents for c in fn.func_closure]
  return dict( zip( fn.func_code.co_freevars, closure_objects ))
