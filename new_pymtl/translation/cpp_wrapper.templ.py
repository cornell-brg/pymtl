from new_pymtl import *
from cffi      import FFI

class {model_name}( Model ):

  def __init__( s ):

    ffi = FFI()
    ffi.cdef('''
      {cdef}
    ''')

    s._cmodule = ffi.dlopen('./{lib_file}')
    s._top     = ffi.new("iface_t *")

    class BundleProxy( PortBundle ):
      flip = False

    {port_defs}

    # Set Input Callbacks
    s._cffi_update = {{}}
    {set_inputs}

  def elaborate_logic( s ):

    #@s.combinational
    #def logic():

    @s.tick
    def seq_logic():

      # Cycle
      s._cmodule.cycle( s.clk, s.reset, s._top )

      # Set outputs
      {set_outputs}

  @property
  def ncycles( s ):
    return s._cmodule.ncycles
