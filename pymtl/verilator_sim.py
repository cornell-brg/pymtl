from translate import VerilogTranslationTool
import v2pymtl


# TODO: figure out a way to replace module instantiation with dummy
#       model that performs translate/verilation with provided
#       parameters and then return the Wrapped/Verilated instance

def translate_class( model_class, config=None ):
  # TODO: currently assumes construct doesn't need any arguments
  #       need to change it to take configuration parameters
  model_inst = model_class()
  model_inst.elaborate()
  verilog_file = model_inst.class_name + '.v'
  VerilogTranslationTool( model_inst, verilog_file )

def verilate( model_class, src_file, config=None ):
  translate_class( model_class )
  v2pymtl.v2pymtl.verilog_to_pymtl( model_class, src_file )
