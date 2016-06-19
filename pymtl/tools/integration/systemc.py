#=======================================================================
# systemc.py
#=======================================================================

from __future__ import print_function

import re
import os
import sys
import inspect
import collections
from copy import deepcopy
from os.path import exists
from shutil  import copyfile
import filecmp
from sc_helper import *

from ...model.metaclasses import MetaCollectArgs

from pymtl import *

#-----------------------------------------------------------------------
# SystemCImportError
#-----------------------------------------------------------------------

class SomeMeta( MetaCollectArgs ):
  def __call__( self, *args, **kwargs ):
    inst = super( SomeMeta, self ).__call__( *args, **kwargs )
    
    # Add os path separator to all source folders

    for i in xrange(len(inst.sourcefolder)):
      if not inst.sourcefolder[i].endswith(os.sep):
        inst.sourcefolder[i] += os.sep
        
    # TODO: currently I don't call translation tool for systemc import,
    # but I guess I need to organize the following piece of code into 
    # some "systemcimporttool"
    
    inst.vcd_file = '__dummy__'
    inst.elaborate()
  
      
    model_name      = inst.class_name
    c_wrapper_file  = model_name + '_sc.cpp'
    py_wrapper_file = model_name + '_sc.py'
    lib_file        = 'lib{}_sc.so'.format( model_name )
    obj_dir         = 'obj_dir_' + model_name + os.sep
    
    # Copy all specified source file to obj folder for later compilation
    # Also try to copy header files by inferring the file extension
    # At the same time check caching status
    #
    # Check the combination of a path, a filename and a extension
    # for both the header and the source. According to C++ 
    # convention the header should have the same filename as the 
    # source file for the compiler to match.
    #
    # The reason why I split the source array and header array into 
    # two groups is for performance -- to hopefully reduce the number
    # of disk inode lookup and disk accesses by breaking the loop
    # when a header/source is found.
    
    extensions = [  [".h", ".hh", ".hpp", ".h++"  ],
                    [".cc", ".cpp", ".c++", ".cxx"] ]
    
    uncached = set()
    src_ext  = {}
    
    if not exists(obj_dir):
      os.mkdir(obj_dir)
    
    for path in inst.sourcefolder:
      for filename in inst.sourcefile:
        file_prefix = path    + filename
        temp_prefix = obj_dir + filename
        
        for group in extensions:
          for ext in group: 
            target_file = file_prefix + ext
            temp_file   = temp_prefix + ext
            temp_obj    = temp_prefix + ".o"
            
            if not exists( target_file ):
              # OK this is not the correct extension.
              continue
            
            if ext.startswith(".c"):
              src_ext[temp_prefix] = ext
                
            # 1. No .o file, then yeah it hasn't been cached.
            # 2. No .c file, probably something unexpected happened.
            # 3. See if the cached file is not up to date.
            
            if not exists( temp_obj ) or \
               not exists( temp_file ) or \
               not filecmp.cmp( temp_file, target_file ):
              
              if exists( temp_obj ):
                os.remove( temp_obj )
              copyfile( target_file, temp_file )
              uncached.add(temp_prefix)
              
            break
    
    # Remake only if we've updated the systemc source

    if not uncached:
      print( "All Cached!")
    else:
      print( "Not Cached", uncached )
      
      # compile all uncached modules
      for x in uncached:
        include_dir = deepcopy( inst.sourcefolder )
        include_dir.append( obj_dir )
        compile_object( x, src_ext[x], obj_dir, include_dir )
    
    # Regenerate the shared library .so file if individual modules are 
    # updated or the .so file is missing.
    
    if not uncached or exists( lib_file ):
      systemc_to_pymtl( inst, c_wrapper_file,
                        lib_file, py_wrapper_file )

    # Use some trickery to import the compiled version of the model
    sys.path.append( os.getcwd() )
    __import__( py_wrapper_file[:-3] )
    imported_module = sys.modules[ py_wrapper_file[:-3] ]

    # Get the model class from the module, instantiate and elaborate it
    model_class = imported_module.__dict__[ model_name ]
    new_inst  = model_class()
    
    #-----
    
    new_inst.vcd_file = None

    new_inst.__class__.__name__  = inst.__class__.__name__
    new_inst.__class__.__bases__ = (SystemCModel,)
    new_inst._args       = inst._args
    new_inst.modulename  = inst.modulename
    new_inst.sourcefile  = inst.sourcefile
    new_inst.sclinetrace = inst.sclinetrace
    new_inst._param_dict = inst._param_dict
    new_inst._port_dict  = inst._port_dict

    # TODO: THIS IS SUPER HACKY. FIXME
    # This copies the user-defined line_trace method from the
    # VerilogModel to the generated Python wrapper.
    try:
      new_inst.__class__.line_trace = inst.__class__.__dict__['line_trace']

      # If we make it here this means the user has set Verilog line
      # tracing to true, but has _also_ defined a PyMTL line tracing, but
      # you can't have both.

      if inst.sclinetrace:
        raise SystemCImportError( "Cannot define a PyMTL line_trace\n"
          "function and also use sclinetrace = True. Must use _either_\n"
          "PyMTL line tracing or use Verilog line tracing." )

    except KeyError:
      pass

    return new_inst

#-----------------------------------------------------------------------
# SystemCModel
#-----------------------------------------------------------------------

class SystemCModel( Model ):
  """
  A PyMTL model for importing hand-written SystemC modules.

  Attributes:
    modulename  Name of the Verilog module to import.
    
    TBA
    
  """
  __metaclass__ = SomeMeta

  modulename   = None
  sourcefile   = None
  sourcefolder = None
  sclinetrace  = False

  _param_dict  = None
  _port_dict   = None

  # set_params: Currently no support for parametrizing SystemC module

  #---------------------------------------------------------------------
  # set_ports
  #---------------------------------------------------------------------
  def set_ports( self, port_dict ):
    """Specify values for each parameter in the imported SystemC module.

    Note that port_dict should be a dictionary that provides a mapping
    from port names (strings) to PyMTL InPort or OutPort objects, for
    examples:

    >>> s.set_ports({
    >>>   'clk':    s.clk,
    >>>   'reset':  s.reset,
    >>>   'input':  s.in_,
    >>>   'output': s.out,
    >>> })
    """

    self._port_dict = collections.OrderedDict( sorted(port_dict.items()) )

  #---------------------------------------------------------------------
  # _auto_init
  #---------------------------------------------------------------------
  def _auto_init( self ):
    """Infer fields not set by user based on Model attributes."""

    if not self.modulename:
      self.modulename = self.__class__.__name__

    if not self.sourcefile:
      file_ = inspect.getfile( self.__class__ )
      self.sourcefile = self.modulename
      
    if not self.sourcefolder:
      file_ = inspect.getfile( self.__class__ )
      self.sourcefolder = os.path.dirname( file_ )
    
    # I added an extra check to only add the prefix if has not already
    # been added. Once we started using Verilog import and then turning
    # around and translated in the importing module this is what I needed
    # to do to get things to work -cbatten.

    if self.scprefix and not self.modulename.startswith(self.scprefix):
      self.modulename = self.scprefix + "_" + self.modulename

    if not self._param_dict:
      self._param_dict = self._args

    if not self._port_dict:
      self._port_dict = { port.name: port for port in self.get_ports() }

