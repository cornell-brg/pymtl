#=======================================================================
# V{model_name}_v.py
#=======================================================================
# This wrapper makes a Verilator-generated C++ model appear as if it
# were a normal PyMTL model.

from pymtl import *
from cffi  import FFI

#-----------------------------------------------------------------------
# {model_name}
#-----------------------------------------------------------------------
class {model_name}( Model ):

  def __init__( s ):

    # initialize FFI, define the exposed interface
    ffi = FFI()
    ffi.cdef('''
      void create_model( void );
      void destroy_model( void );
      void eval( void );

      {port_decls}
    ''')

    # import the shared library containing the model and construct it
    s._model = ffi.dlopen('./{lib_file}')
    s._model.create_model()

    # dummy class to emulate PortBundles
    class BundleProxy( PortBundle ):
      flip = False

    # define the port interface
    {port_defs}

  def __del__( s ):
    s._model.destroy_model()

  def elaborate_logic( s ):

    @s.combinational
    def logic():

      # set inputs
      {set_inputs}

      # execute combinational logic
      s._model.eval()

      # set outputs
      # FIXME: currently write all outputs, not just combinational outs
      {set_comb}

    @s.posedge_clk
    def tick():

      s._model.clk[0] = 0
      s._model.eval()
      s._model.clk[0] = 1
      s._model.eval()

      # double buffer register outputs
      # FIXME: currently write all outputs, not just registered outs
      {set_next}

