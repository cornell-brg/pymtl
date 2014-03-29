from new_pymtl import *
from cffi      import FFI

class {model_name}( Model ):

  def __init__( s, cmodule, ffi ):

    s._cmodule = cmodule
    s._ffi     = ffi
    s._top     = ffi.new("iface_t *")

    class BundleProxy( object ):
      pass

    {port_defs}

  def elaborate_logic( s ):

    #@s.combinational
    #def logic():

    @s.posedge_clk
    def tick():

      # Set inputs
      {set_inputs}

      # Cycle
      self._cmodule.cycle( self.clk, self.reset, self._top )
  
      # Set outputs
      {set_outputs}

  @property
  def ncycles( self ):
    return self._cmodule.ncycles
