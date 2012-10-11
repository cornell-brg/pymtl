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
    self.in0  = InPort ( 4 )
    self.in1  = InPort ( 1 )
    self.out0 = OutPort( 4 )
    self.out1 = OutPort( 1 )
    connect( self.in0, self.out0 )
    connect( self.in1, self.out1 )

def test_In_Out():
  run_translate_test( In_Out )

#-------------------------------------------------------------------------
# InPort to OutPort Slice
#-------------------------------------------------------------------------

class In_OutSL(Model):
  def __init__(self):
    self.in0 = InPort ( 2 )
    self.in1 = InPort ( 1 )
    self.out = OutPort( 6 )
    connect( self.in0, self.out[0:2] )
    connect( self.in0, self.out[2:4] )
    connect( self.in1, self.out[4]   )
    connect( self.in1, self.out[5]   )

def test_In_OutSL():
  run_translate_test( In_OutSL )

#-------------------------------------------------------------------------
# InPort Slice to OutPort
#-------------------------------------------------------------------------

class InSL_Out(Model):
  def __init__(self):
    self.in_ = InPort ( 4 )
    self.out0 = OutPort( 3 )
    self.out1 = OutPort( 1 )
    connect( self.in_[0:3], self.out0 )
    connect( self.in_[3],   self.out1 )

def test_InSL_Out():
  run_translate_test( InSL_Out )

#-------------------------------------------------------------------------
# InPort Slice to OutPort Slice
#-------------------------------------------------------------------------

class InSL_OutSL(Model):
  def __init__(self):
    self.in_ = InPort ( 4 )
    self.out = OutPort( 4 )
    connect( self.in_[0:3], self.out[1:4] )
    connect( self.in_[3],   self.out[0]   )

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

class In_sub_Out(Model):
  def __init__(self):
    self.in_ = InPort ( 4 )
    self.out = OutPort( 4 )
    self.sub = SubMod (   )

    connect( self.in_, self.sub.in_ )
    connect( self.out, self.sub.out )

def test_In_sub_Out():
  run_translate_test( In_sub_Out )

#-------------------------------------------------------------------------
# InPort Slice to Submodel to OutPort Slice
#-------------------------------------------------------------------------

class InSL_sub_OutSL(Model):
  def __init__(self):
    self.in_  = InPort ( 8 )
    self.out  = OutPort( 8 )
    self.sub0 = SubMod (   )
    self.sub1 = SubMod (   )

    connect( self.in_[0:4], self.sub0.in_ )
    connect( self.out[0:4], self.sub0.out )
    connect( self.in_[4:8], self.sub1.in_ )
    connect( self.out[4:8], self.sub1.out )

def test_InSL_sub_OutSL():
  run_translate_test( InSL_sub_OutSL )

#-------------------------------------------------------------------------
# InPort to Submodel Slices to OutPort
#-------------------------------------------------------------------------

class In_subSL_Out(Model):
  def __init__(self):
    self.in0  = InPort ( 2 )
    self.in1  = InPort ( 2 )
    self.out0 = OutPort( 2 )
    self.out1 = OutPort( 2 )
    self.sub0 = SubMod (   )

    connect( self.in0,  self.sub0.in_[0:2] )
    connect( self.in1,  self.sub0.in_[2:4] )
    connect( self.out0, self.sub0.out[2:4] )
    connect( self.out1, self.sub0.out[0:2] )

def test_In_subSL_Out():
  run_translate_test( In_subSL_Out )

#-------------------------------------------------------------------------
# InPort Slice to Submodel Slices to OutPort Slice
#-------------------------------------------------------------------------

class InSL_subSL_OutSL(Model):
  def __init__(self):
    self.in_  = InPort ( 4 )
    self.out  = OutPort( 4 )
    self.sub0 = SubMod (   )

    connect( self.in_[0:3], self.sub0.in_[1:4] )
    connect( self.in_[3],   self.sub0.in_[0]   )
    connect( self.out[0:3], self.sub0.out[0:3] )
    connect( self.out[3],   self.sub0.out[3]   )

def test_InSL_subSL_OutSL():
  run_translate_test( InSL_subSL_OutSL )

#-------------------------------------------------------------------------
# InPort to Submodel to Submodel to OutPort Slice
#-------------------------------------------------------------------------

class In_sub_sub_Out(Model):
  def __init__(self):
    self.in_  = InPort ( 4 )
    self.out  = OutPort( 4 )
    self.sub0 = SubMod (   )
    self.sub1 = SubMod (   )

    connect( self.in_,        self.sub0.in_ )
    connect( self.sub0.out,   self.sub1.in_ )
    connect( self.out,        self.sub1.out )

def test_In_sub_sub_Out():
  run_translate_test( In_sub_sub_Out )

#-------------------------------------------------------------------------
# InPort to Submodel Slices to Submodel Slices to OutPort Slice
#-------------------------------------------------------------------------

class In_subSL_subSL_Out(Model):
  def __init__(self):
    self.in_  = InPort ( 4 )
    self.out  = OutPort( 4 )
    self.sub0 = SubMod (   )
    self.sub1 = SubMod (   )

    connect( self.in_,           self.sub0.in_      )
    connect( self.sub0.out[1:4], self.sub1.in_[0:3] )
    connect( self.sub0.out[0],   self.sub1.in_[3]   )
    connect( self.out,           self.sub1.out      )

def test_In_subSL_subSL_Out():
  run_translate_test( In_subSL_subSL_Out )

