from pymtl import *
from cffi  import FFI

class {model_name}( Model ):

  def __init__( s ):

    ffi = FFI()
    ffi.cdef('''
      void create_model( void );
      void destroy_model( void );
      void eval( void );
      void trace( void );

      {port_decls}
    ''')

    s._model = ffi.dlopen('./{lib_file}')
    s._model.create_model()

    class BundleProxy( PortBundle ):
      flip = False

    {port_defs}

  def __del__( s ):
    s._model.destroy_model()

  def elaborate_logic( s ):
    @s.combinational
    def logic():

      # Set reset
      s._model.reset[0] = s.reset

      # Set inputs
      {set_inputs}

      # Execute combinational logic
      s._model.eval()

      # Set outputs
      {set_comb}

    @s.posedge_clk
    def tick():

      # Tick and capture VCD output
      s._model.eval()
      s._model.trace()

      # Set clk high and repeat
      s._model.clk[0] = 1
      s._model.eval()
      s._model.trace()

      {set_next}

      s._model.clk[0] = 0

