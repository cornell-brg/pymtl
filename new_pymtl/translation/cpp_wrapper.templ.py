from new_pymtl import *
from cffi      import FFI

class {model_name}( Model ):

  def __init__( s, cmodule, ffi ):

    s._cmodule = cmodule
    s._ffi     = ffi
    s._top     = ffi.new("iface_t *")

    class BundleProxy( PortBundle ):
      flip = False

    {port_defs}

  def elaborate_logic( s ):

    #@s.combinational
    #def logic():

    @s.posedge_clk
    def tick():

      # Set inputs
      {set_inputs}

      # Cycle
      s._cmodule.cycle( s.clk, s.reset, s._top )

      # Set outputs
      {set_outputs}

  @property
  def ncycles( s ):
    return s._cmodule.ncycles
