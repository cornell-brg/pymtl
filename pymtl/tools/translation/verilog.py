#=======================================================================
# verilog.py
#=======================================================================

import sys
import collections
import tempfile

from subprocess         import check_output, STDOUT, CalledProcessError
from verilog_structural import *
from verilog_behavioral import translate_logic_blocks

#-----------------------------------------------------------------------
# translate
#-----------------------------------------------------------------------
# Generates Verilog source from a PyMTL model.
def translate( model, o=sys.stdout ):

  # List of models to translate
  translation_queue = collections.OrderedDict()

  # Utility function to recursively collect all submodels in design
  def collect_all_models( m ):
    # Add the model to the queue
    translation_queue[ m.class_name ] = m

    for subm in m.get_submodules():
      collect_all_models( subm )

  # Collect all submodels in design and translate them
  collect_all_models( model )
  for k, v in translation_queue.items():
    translate_module( v, o )

#-----------------------------------------------------------------------
# translate_module
#-----------------------------------------------------------------------
def translate_module( model, o ):

  # Visit concurrent blocks in design
  logic, symtab = translate_logic_blocks( model )

  print >> o, header             ( model,  symtab ),
  print >> o, start_mod.format( model.class_name )
  # Signal Declarations
  print >> o, port_declarations  ( model,  symtab ),
  print >> o, wire_declarations  ( model,  symtab ),
  print >> o, create_declarations( model, *symtab ),
  # Structural Verilog
  print >> o, submodel_instances ( model,  symtab ),
  print >> o, signal_assignments ( model,  symtab )
  # Array Declarations
  print >> o, array_declarations ( model,  symtab ),
  # Behavioral Verilog
  print >> o, logic
  print >> o, end_mod  .format( model.class_name )
  print >> o

#-----------------------------------------------------------------------
# check_compile
#-----------------------------------------------------------------------
compiler = 'iverilog -g2005 -Wall -Wno-sensitivity-entire-vector'
def check_compile( model ):

  model.elaborate()

  with tempfile.NamedTemporaryFile(suffix='.v') as output:

    translate( model, output )
    output.flush()
    cmd  = '{} {}'.format( compiler, output.name )

    try:

      result = check_output( cmd.split() , stderr=STDOUT )
      output.seek(0)
      verilog_src = output.read()
      print
      print verilog_src

    except CalledProcessError as e:

      output.seek(0)
      verilog_src = output.read()

      raise Exception( 'Module did not compile!\n\n'
                       'Command:\n {}\n\n'
                       'Error:\n {}'
                       'Source:\n {}'
                       .format( ' '.join(e.cmd), e.output, verilog_src )
                     )

