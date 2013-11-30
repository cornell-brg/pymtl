#=========================================================================
# verilog.py
#=========================================================================

import sys
import collections

from verilog_structural import *

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

#-------------------------------------------------------------------------
# translate_module
#-------------------------------------------------------------------------
def translate_module( model, o ):

  print >> o, header   .format( model.class_name )
  print >> o, start_mod.format( model.class_name )

  # Structural Verilog
  port_declarations ( model, o )
  #wire_declarations ( model, o )
  submodel_instances( model, o )
  signal_assignments( model, o )

  # Behavioral Verilog
  #translate_logic_blocks( model, o )

  print >> o, end_mod  .format( model.class_name )
  print >> o
