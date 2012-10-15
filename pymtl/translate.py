#=========================================================================
# Verilog Translation Tool
#=========================================================================
"""Tools for translating ConnectionGraphs and  Python Logic into HDLs"""

import sys
import collections

from translate_cgraph import ModuleToVerilog

#------------------------------------------------------------------------
# Verilog Translation Tool
#-------------------------------------------------------------------------

class VerilogTranslationTool(object):

  #-----------------------------------------------------------------------
  # Constructor
  #-----------------------------------------------------------------------

  def __init__(self, model, o=sys.stdout):
    """Construct a Verilog translator from a MTL model."""

    # TODO: call elaborate on model?
    if not model.is_elaborated():
      msg  = "cannot initialize {0} tool.\n".format(self.__class__.__name__)
      msg += "Provided model has not been elaborated yet!!!"
      raise Exception(msg)

    self.to_translate = collections.OrderedDict()

    # Take either a string or a output stream
    if isinstance(o, str):
      o = open(o, 'w')

    # Find all the modules we need to translate in the hierarchy
    # TODO: use ordered list?
    self.collect_models( model )

    # Translate each Module Class
    for class_name, class_inst in self.to_translate.items():
      ModuleToVerilog( class_inst, o )

  #-----------------------------------------------------------------------
  # Collect Modules
  #-----------------------------------------------------------------------

  def collect_models(self, target):
    """Create an ordered dict of all models we need to translate."""
    if not target.class_name in self.to_translate:
      self.to_translate[ target.class_name ] = target
      for m in target._submodules:
        self.collect_models( m )
