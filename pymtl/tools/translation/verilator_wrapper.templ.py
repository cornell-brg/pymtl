#=======================================================================
# V{model_name}_v.py
#=======================================================================
# This wrapper makes a Verilator-generated C++ model appear as if it
# were a normal PyMTL model.

import os

from pymtl import *
from cffi  import FFI

#-----------------------------------------------------------------------
# {model_name}
#-----------------------------------------------------------------------
class {model_name}( Model ):
  id_ = 0

  def __init__( s, vcd_file='' ):

    # initialize FFI, define the exposed interface
    ffi = FFI()
    ffi.cdef('''
      typedef struct {{

        // Exposed port interface
        {port_decls}

        // Verilator model
        void * model;

      }} V{model_name}_t;

      V{model_name}_t * create_model( const char * );
      void destroy_model( V{model_name}_t *);
      void eval( V{model_name}_t * );

    ''')

    # set vcd_file attribute, give verilator_vcd_file a slightly
    # different name so PyMTL .vcd and Verilator .vcd can coexist
    s.vcd_file         = vcd_file
    verilator_vcd_file = vcd_file
    if vcd_file:
      filen, ext         = os.path.splitext( vcd_file )
      verilator_vcd_file = '{{}}.verilator{{}}{{}}'.format(filen, s.id_, ext)

    # import the shared library containing the model and construct it
    s._ffi = ffi.dlopen('./{lib_file}')
    s._m   = s._ffi.create_model( ffi.new("char[]", verilator_vcd_file) )

    # dummy class to emulate PortBundles
    class BundleProxy( PortBundle ):
      flip = False

    # define the port interface
    {port_defs}

    # increment instance count
    {model_name}.id_ += 1

  def __del__( s ):
    s._ffi.destroy_model( s._m )

  def elaborate_logic( s ):

    @s.combinational
    def logic():

      # set inputs
      {set_inputs}

      # execute combinational logic
      s._ffi.eval( s._m )

      # set outputs
      # FIXME: currently write all outputs, not just combinational outs
      {set_comb}

    @s.posedge_clk
    def tick():

      s._m.clk[0] = 0
      s._ffi.eval( s._m )
      s._m.clk[0] = 1
      s._ffi.eval( s._m )

      # double buffer register outputs
      # FIXME: currently write all outputs, not just registered outs
      {set_next}

