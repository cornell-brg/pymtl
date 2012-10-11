#=========================================================================
# Basic Connection Graph Translation Test
#=========================================================================

from model import *
from translate_new import *

import os

#-------------------------------------------------------------------------
# Translation Test Function
#-------------------------------------------------------------------------

def run_translate_test( model_class ):

  # Generate the model
  model = model_class()
  model.elaborate()

  #  if debug_verbose: debug_utils.port_walk(model)

  # Create the Verilog file
  temp_file = model.class_name + '.v'
  fd = open( temp_file, 'w' )
  code = VerilogTranslationTool( model, fd )
  fd.close()

  # Check that it compiles cleanly with iverilog
  compile_cmd = ("iverilog -g2005 -Wall -Werror -Wno-sensitivity-entire-vector"
                  "-Wno-sensitivity-entire-array " + temp_file)
  x = os.system( compile_cmd )
  assert x == 0

#-------------------------------------------------------------------------
# InPort to OutPort
#-------------------------------------------------------------------------

class In_Out(Model):
  def __init__(self):
    self.in_ = InPort ( 4 )
    self.out = OutPort( 4 )
    connect( self.in_, self.out )

def test_In_Out():
  run_translate_test( In_Out )

#-------------------------------------------------------------------------
# InPort to OutPort Slice
#-------------------------------------------------------------------------

class In_OutSL(Model):
  def __init__(self):
    self.in_ = InPort ( 2 )
    self.out = OutPort( 4 )
    connect( self.in_, self.out[0:2] )
    connect( self.in_, self.out[2:4] )

def test_In_OutSL():
  run_translate_test( In_OutSL )

#-------------------------------------------------------------------------
# InPort Slice to OutPort
#-------------------------------------------------------------------------

class InSL_Out(Model):
  def __init__(self):
    self.in_ = InPort ( 4 )
    self.out = OutPort( 2 )
    connect( self.in_[0:2], self.out )

def test_InSL_Out():
  run_translate_test( InSL_Out )

#-------------------------------------------------------------------------
# InPort Slice to OutPort Slice
#-------------------------------------------------------------------------

class InSL_OutSL(Model):
  def __init__(self):
    self.in_ = InPort ( 4 )
    self.out = OutPort( 4 )
    connect( self.in_[0:2], self.out[2:4] )
    connect( self.in_[2:4], self.out[0:2] )

def test_InSL_OutSL():
  run_translate_test( InSL_OutSL )

#-------------------------------------------------------------------------
# Dummy SubModel
#-------------------------------------------------------------------------

class SubMod(Model):
  def __init__(self):
    self.in_ = InPort ( 4 )
    self.out = OutPort( 4 )

#-------------------------------------------------------------------------
# InPort to Submodel to OutPort
#-------------------------------------------------------------------------
class In_S_Out(Model):
  def __init__(self):
    self.in_ = InPort ( 4 )
    self.out = OutPort( 4 )
    self.sub = SubMod (   )

    connect( self.in_, self.sub.in_ )
    connect( self.out, self.sub.out )

def test_In_S_Out():
  run_translate_test( In_S_Out )



