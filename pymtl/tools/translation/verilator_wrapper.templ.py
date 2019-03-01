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

  def __init__( s ):

    # initialize FFI, define the exposed interface
    s.ffi = FFI()
    s.ffi.cdef('''
      typedef struct {{

        // Exposed port interface
        {port_decls}

        // Verilator model
        void * model;

        // VCD state
        int _vcd_en;

      }} V{model_name}_t;

      V{model_name}_t * create_model( const char * );
      void destroy_model( V{model_name}_t *);
      void eval( V{model_name}_t * );
      void trace( V{model_name}_t *, char * );

    ''')

    # Import the shared library containing the model. We defer
    # construction to the elaborate_logic function to allow the user to
    # set the vcd_file.

    s._ffi = s.ffi.dlopen('./{lib_file}')
    s._m = None

    # dummy class to emulate PortBundles
    class BundleProxy( PortBundle ):
      flip = False

    # define the port interface
    {port_defs}

    # increment instance count
    {model_name}.id_ += 1

    # Defer vcd dumping until later
    s.vcd_file = None

    # Buffer for line tracing
    s._line_trace_str = s.ffi.new("char[512]")
    s._convert_string = s.ffi.string

  def __del__( s ):
    # Cannot destroy if _m doesn't exist yet
    if s._m:
      s._ffi.destroy_model( s._m )

  def elaborate_logic( s ):

    # Give verilator_vcd_file a slightly different name so PyMTL .vcd and
    # Verilator .vcd can coexist

    verilator_vcd_file = ""
    if s.vcd_file:
      filen, ext         = os.path.splitext( s.vcd_file )
      verilator_vcd_file = '{{}}.verilator{{}}'.format(filen, ext)

    # Construct the model.

    s._m = s._ffi.create_model( s.ffi.new("char[]", verilator_vcd_file) )

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

  def line_trace( s ):
    if {vlinetrace}:
      s._ffi.trace( s._m, s._line_trace_str )
      return s._convert_string( s._line_trace_str )
    else:
      return ""

