#=======================================================================
# {class_name}_sc.py
#=======================================================================
# This wrapper makes a SystemC model appear as if it
# were a normal PyMTL model.

import os

from pymtl import *
from cffi  import FFI

#-----------------------------------------------------------------------
# {class_name}
#-----------------------------------------------------------------------
class {class_name}( Model ):
  id_ = 0

  def __init__( s ):

    # initialize FFI, define the exposed interface
    s.ffi = FFI()
    s.ffi.cdef({cdef})

    # Import the shared library containing the model. We defer
    # construction to the elaborate_logic function to allow the user to
    # set the vcd_file.

    s._ffi = s.ffi.dlopen('./lib{}_sc.so'.format( class_name ))

    # dummy class to emulate PortBundles
    class BundleProxy( PortBundle ):
      flip = False

    # define the port interface
    {port_defs}

    # increment instance count
    {class_name}.id_ += 1

    # Defer vcd dumping until later
    s.vcd_file = None

    # Buffer for line tracing
    s._line_trace_str = s.ffi.new("char[512]")
    s._convert_string = s.ffi.string

  def __del__( s ):
    s._ffi.destroy( s._m )

  def elaborate_logic( s ):

    # Give verilator_vcd_file a slightly different name so PyMTL .vcd and
    # Verilator .vcd can coexist

    verilator_vcd_file = ""
    if s.vcd_file:
      filen, ext         = os.path.splitext( s.vcd_file )
      verilator_vcd_file = '{{}}.verilator{{}}{{}}'.format(filen, s.id_, ext)

    # Construct the model.

    s._m = s._ffi.create()

    @s.combinational
    def logic():
      
      m = s._m
      
      {set_inputs}

      s._ffi.sim_comb()

      {set_comb}

    @s.posedge_clk
    def tick():

      s._ffi.sim_cycle()
      
      m = s._m
      
      {set_next}

  def line_trace( s ):
    if {sclinetrace}:
      s._ffi.trace( s._m, s._line_trace_str )
      return s._convert_string( s._line_trace_str )
    else:
      return ""
