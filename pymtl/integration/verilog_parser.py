#=======================================================================
# verilog_parser
#=======================================================================
# Resources:
#
# - http://pyparsing.wikispaces.com/HowToUsePyparsing
# - http://ingeneur.wordpress.com/2007/10/29/pyparsing-with-verilog/
# - http://eikke.com/pyparsing-introduction-bnf-to-code/

from pyparsing import Literal, Word, Keyword, alphanums, Regex
from pyparsing import Group, ZeroOrMore, OneOrMore, oneOf, delimitedList
from pyparsing import Optional, SkipTo, StringEnd, restOfLine, LineEnd
from pyparsing import cppStyleComment, dblSlashComment
from pyparsing import ParseException, Suppress
import sys

#-----------------------------------------------------------------------
# header_parser
#-----------------------------------------------------------------------
# A simple parser for Verilog module interfaces. Collects class
# name, parameter names, and port names.
#
# Eventually maybe clean this up and instead euse one of the these
# existing parsers:
#
# - https://github.com/gburdell/parser/blob/master/src/parser/sv/sysvlog.g
# - https://github.com/steveicarus/iverilog/blob/master/parse.y
# - http://cpansearch.perl.org/src/WSNYDER/Verilog-Perl-3.403/Parser/VParseBison.y
# - https://code.google.com/p/vtr-verilog-to-routing/source/browse/trunk/ODIN_II/SRC/verilog_bison.y
# - https://github.com/yellekelyk/PyVerilog/blob/master/verilogParse.py
# - https://github.com/kristofferkoch/metav/blob/master/metav/parse.py
#
def header_parser():

  identifier  = Regex("[a-zA-Z_][a-zA-Z0-9_\$]*")
  comment     = cppStyleComment.suppress()

  size = Group(
    Optional( Suppress('[') + SkipTo(']') + Suppress(']') )
  )

  # Params

  end_param = Literal(',') + 'parameter' | Literal(')') + '('
  ptype     = Optional( oneOf('integer real realtime time') )

  # NOTE: this isn't completely right, good enough for parsing valid Verilog
  param = Group(
    'parameter' + ptype + size + identifier +
    Suppress('=') + SkipTo(end_param)
  )

  list_of_params = Group(
    Suppress('#(') + delimitedList( param ) + Suppress(')')
  )

  # Ports

  dir_    = Optional( oneOf('input output inout') )
  type_   = Optional( oneOf('wire reg') )
  port    = Group(
    dir_ + type_ + size + identifier
  )

  list_of_ports = Group(
    Suppress('(') + delimitedList( port ) + Suppress(')')
  )

  # Module

  module_identifier = identifier

  module = Group(
    Suppress('module') +
    module_identifier('module_name') +
    Optional( list_of_params('params') )  +
    Optional( list_of_ports ('ports' ) )  +
    Suppress(';') +
    SkipTo('endmodule') + Suppress('endmodule')
  )

  # Debug
  #print
  #module_identifier.setParseAction( dbg('modname') )#.setDebug()
  #param            .setParseAction( dbg('param')  )#.setDebug()
  #port             .setParseAction( dbg('port' )  )#.setDebug()
  #module           .setParseAction( dbg('module', 1) )#.setDebug()

  file_ = SkipTo('module', ignore=comment ).suppress() + \
          OneOrMore( module ).ignore( comment )        + \
          SkipTo( StringEnd() ).suppress()

  return file_

#-----------------------------------------------------------------------
# Notes from BNF
#-----------------------------------------------------------------------
# http://staff.ustc.edu.cn/~songch/download/IEEE.1364-2005.pdf
# http://boydtechinc.com/etf/archive/att-2157/01-1364_Errata_12Nov.pdf
# http://www.verilog.com/VerilogBNF.html
#
#  module_declaration ::=
#      { attribute_instance } module_keyword module_identifier
#        [ module_parameter_port_list ]
#        list_of_ports ;
#        { module_item }
#        endmodule
#    | { attribute_instance } module_keyword module_identifier
#        [ module_parameter_port_list ]
#        [ list_of_port_declarations ] ;
#        { non_port_module_item }
#        endmodule
#
#
# identifier ::=
#     simple_identifier
#   | escaped_identifier
#
# simple_identifier  ::= [ a-zA-Z_ ] { [ a-zA-Z0-9_$ ] }
# escaped_identifier ::= \ {Any_ASCII_character_except_white_space} white_space
# white_space        ::= space | tab | newline | eof
#
# module_identifier      ::= identifier
# inout_port_identifier  ::= identifier
# input_port_identifier  ::= identifier
# output_port_identifier ::= identifier
# parameter_identifier   ::= identifier
# port_identifier        ::= identifier
#
#
# module_keyword ::= module | macromodule
#
# module_parameter_port_list ::=
#    #( parameter_declaration { , parameter_declaration } )
#
# list_of_ports ::= ( port { , port } )
#
# list_of_port_declarations ::=
#      ( port_declaration { , port_declaration } )
#    | ( )
#
# port :=
#     [ port_expression ]
#   | . port_identifier ( [ port_expression ] )
#
# port_expression ::=
#     port_reference
#   | { port_reference { , port_reference } }
#
# port_reference ::= port_identifier [ [ constant_range_expression ] ]
#
# port_declaration ::=
#     {attribute_instance} inout_declaration
#   | {attribute_instance} input_declaration
#   | {attribute_instance} output_declaration
#
# inout_declaration ::=
#    inout  [ net_type ] [ signed ] [ range ] list_of_port_identifiers
#
# input_declaration ::=
#    input  [ net_type ] [ signed ] [ range ] list_of_port_identifiers

# output_declaration ::=
#    output [ net_type ] [ signed ] [ range ] list_of_port_identifiers
#  | output reg [ signed ] [ range ] list_of_variable_port_identifiers
#  | output output_variable_type list_of_variable_port_identifiers
#
# list_of_port_identifiers ::= port_identifier { , port_identifier }
#
# list_of_variable_port_identifiers ::=
#     port_identifier [ = constant_expression ]
#      { , port_identifier [ = constant_expression ] }
#
# parameter_declaration ::=
#     parameter [ signed ] [ range ] list_of_param_assignments
#   | parameter parameter_type list_of_param_assignments
#
# list_of_param_assignments ::=
#     param_assignment { , param_assignment }
#
# param_assignment ::=
#     parameter_identifier = constant_mintypmax_expression
#
# parameter_type ::= integer | real | realtime | time
#
# range ::= [ msb_constant_expression : lsb_constant_expression ]
#
# constant_range_expression ::=
#     constant_expression
#   | msb_constant_expression : lsb_constant_expression
#   | constant_base_expression +: width_constant_expression
#   | constant_base_expression -: width_constant_expression
#
# msb_constant_expression   ::= constant_expression
# lsb_constant_expression   ::= constant_expression
# width_constant_expression ::= constant_expression
#
# constant_mintypmax_expression ::=
#     constant_expression
#   | constant_expression : constant_expression : constant_expression
#
# constant_expression ::=
#     constant_primary
#   | unary_operator { attribute_instance } constant_primary
#   | constant_expression binary_operator { attribute_instance }
#       constant_expression
#   | constant_expression ? { attribute_instance }
#       constant_expression : constant_expression
#
# unary_operator ::=
#     + | - | ! | ~ | & | ~& | | | ~| | ^ | ~^ | ^~
#
# constant_primary ::=
#     number
#   | parameter_identifier [ [ constant_range_expression ] ]
#   | specparam_identifier [ [ constant_range_expression ] ]
#   | constant_concatenation
#   | constant_multiple_concatenation
#   | constant_function_call
#   | constant_system_function_call
#   | ( constant_mintypmax_expression )
#   | string

#-----------------------------------------------------------------------
# dbg
#-----------------------------------------------------------------------
# Utility debugging method
def dbg( label, tkn_id=None ):
  def action( s, tkn, smt ):
    if tkn_id: print label, smt[tkn_id]
    else:      print label, smt
  return action

#-----------------------------------------------------------------------
# __main__
#-----------------------------------------------------------------------
if __name__ == '__main__' :
  if not len(sys.argv) == 2 :
    print "Usage : python %s <filename>.v" %(sys.argv[0])
    sys.exit()
  source = create_parser()
  source.parseFile(sys.argv[1])
