===============================================================================
Importing Verilog Components into PyMTL
===============================================================================

PyMTL provides facilities for importing Verilog source for testing and
simulation within the PyMTL framework. This is done by compiling the user's
Verilog source into a C++ simulator using the Verilator open source toolchain,
and wrapping this C++ code in a PyMTL harness.

-------------------------------------------------------------------------------
Steps for Importing Verilog
-------------------------------------------------------------------------------

In order to import Verilog, the user must perform the following steps:

1. Write/modify Verilog source to meet the PyMTL naming and style restrictions.
2. Write a PyMTL VerilogModel wrapper.
3. Import and instantiate the VerilogModel component.

Once these three steps are performed, users should be able to interact with the
VerilogModel component as if it were a normal PyMTL model.

-------------------------------------------------------------------------------
Creating a VerilogModel Wrapper using Name Inference
-------------------------------------------------------------------------------

The PyMTL VerilogModel import mechanism enables the creation of very concise
Verilog module wrappers provided the Verilog source and PyMTL wrapper conform
to special naming guidelines and file organization restrictions. These naming
guidelines allow the VerilogModel import mechanism to infer file, module, port,
and parameter names of the underlying Verilog source code.

Verilog components which do not meet these restrictions cannot use the name
inference facilities of the VerilogModel importer. Creating wrappers for these
modules using a manual mapping approach is discussed later in this document.

Given a Verilog module named ``Foo``, the use of the "name inference" mechanism
requires that the source code of ``Foo`` and the associated PyMTL wrapper meet
the following criteria:

1. The definition of Verilog module ``Foo`` must be in a Verilog source file
   named ``Foo.v``.
   (The Verilog source file name must match the Verilog module name).
2. The Verilog module must have ``clk`` and ``reset`` ports (even if unused).
3. The PyMTL wrapper class must also be named ``Foo``.
   (The PyMTL wrapper class name must match the Verilog module name).
4. The PyMTL wrapper source file must be named ``Foo.py``.
   (The PyMTL wrapper source file must match the PyMTL wrapper class name).
5. The PyMTL wrapper class must subclass the VerilogModel class.
6. The constructor parameters of the PyMTL wrapper class must match the
   parameters of the Verilog module (both the number of parameters and the
   names of the parameters).
7. The ports of the PyMTL wrapper class must match the ports of the Verilog
   module (this includes the port names, port directions, and port bitwidths).

-------------------------------------------------------------------------------
Example: A VerilogModel Wrapper using Name Inference
-------------------------------------------------------------------------------

Given a Verilog file named ``EnResetRegVRTL.v`` containing the following
(incomplete) source code::

  //===========================================================================
  // EnResetRegVRTL.v
  //===========================================================================
  // Note that the Verilog source file name matches the Verilog module name.

  module EnResetRegVRTL
  #(
   parameter nbits       = 1,
   parameter reset_value = 0
  )(
   input              en,
   input  [nbits-1:0] d,
   output [nbits-1:0] q,

   // Note that the Verilog module **must** have clk and resets ports.
   input              clk,
   input              reset
  );
    ...
  endmodule

A PyMTL Verilog wrapper using name inference would look like this::

  #============================================================================
  # EnResetRegVRTL.py
  #============================================================================
  # Note that the PyMTL source file name matches the PyMTL class name.

  from pymtl import *

  # Note that the PyMTL wrapper class name matches the Verilog module name.
  # Also note that the PyMTL wrapper class subclasses from VerilogModel.

  class EnResetRegVRTL( VerilogModel ):

   # Note that the __init__ argument names match the Verilog module parameters.

   def __init__( s, nbits, reset_value=0 ):

     # Note that the name, direction, and bitwidth of PyMTL model's Ports match
     # the port specifications of the Verilog module.

     s.en  = InPort ( 1 )
     s.d   = InPort ( nbits )
     s.q   = OutPort( nbits )

Once the VerilogModel is correctly specified, it can be imported and tested in
a py.test testing harness like so::

  #============================================================================
  # EnResetRegVRTL_test.py
  #============================================================================

  import pytest

  from pymtl          import *
  from EnResetRegVRTL import EnResetRegVRTL

  #----------------------------------------------------------------------------
  # setup
  #----------------------------------------------------------------------------
  def setup( model, test_verilog, dump_vcd='' ):
    '''Helper function to setup the DUT and return a simulator.'''

    model.vcd_file = dump_vcd

    if test_verilog: m = TranslationTool( model )
    else:             m = model

    m.elaborate()
    sim = SimulationTool( m )
    return m, sim

  #----------------------------------------------------------------------------
  # test_EnResetRegVRTL
  #----------------------------------------------------------------------------
  @pytest.mark.parametrize( "nbits,rst", [(4,0), (128,8)] )
  def test_EnResetRegVRTL( test_verilog, nbits, rst ):
    '''Test to verify the import of the Verilog module EnResetRegVRTL'''

     # create a simulator for the Verilog component

     m, sim = setup( EnResetRegVRTL(nbits,rst), test_verilog )
     sim.reset()

     # test the Verilog source!

     assert m.q == rst
     last = rst

     for i in range( 10 ):
       en   = random.randint(0,1)
       last = i if en else last
       m.d .value = i
       m.en.value = en
       sim.cycle()
       assert m.q == last

To run the above test file, use py.test at the commandline::

  > cd ${PATH_TO_PYMTL}/build
  > py.test ../verilog_wrappers/EnResetRegVRTL_test.py --verbose
  > py.test ../verilog_wrappers/EnResetRegVRTL_test.py --verbose --test-verilog

-------------------------------------------------------------------------------
Creating a VerilogModel Wrapper Manually
-------------------------------------------------------------------------------

In some cases the user may prefer not to modify the Verilog source to meet
naming conventions, or may want more power over the mapping of identifiers from
the PyMTL wrapper to the Verilog source code. In these scenarios the wrapper
author can manually specify the Verilog file, module, parameter, and port names
using the VerilogModule attributes and methods described below:

- ``modulename``: a class or instance attribute which specifies the name of the
  Verilog module to be imported.
- ``sourcefile``: a class or instance attribute which specifies the file from
  which the Verilog module should be imported (must be a fully qualified path).
- ``set_params()``: a method that takes a dictionary mapping of Verilog
  parameter names to desired parameter values.
- ``set_ports()``: a method that takes a dictionary mapping of Verilog port
  names to PyMTL ports.

Users can use all or only some of the above configuration attributes/methods
when writing PyMTL wrappers for their Verilog modules. Configuration details
which are not explicitly specified will be set using the name inference rules
described above. However, note that the VerilogModule import mechanism will
**not** use name inference for only some parameters (ports) if the
``set_params()`` (``set_ports()``) methods are used: a complete specification
of all parameters (ports) is required if ``set_params()`` (``set_ports()``) is
called!  Also note that the user must explicitly specify the mapping of ``clk``
and ``reset`` ports which are implicitly added to all PyMTL models.

-------------------------------------------------------------------------------
Example: Creating a VerilogModel Wrapper Manually to use PortBundles
-------------------------------------------------------------------------------

One example use case where a user may want to use a manual specification rather
than name inference is when writing a PyMTL wrapper that exposes a PortBundle
interface. Because Verilog has no notion of PortBundles, type inference cannot
be used and the wrapper author must manually map PyMTL ports to their proper
counterparts in the Verilog source file. An example is shown below.

Given a Verilog file named ``PortBundleExVRTL.v`` containing the following
(incomplete) source code::

  //===========================================================================
  // PortBundleExVRTL.v
  //===========================================================================

  module PortBundleExVRTL
  #( parameter nbits = 1 )
  (
   input              clk,
   input              reset,

   input  [nbits-1:0] in_msg,
   input              in_val,
   output             in_rdy,

   output [nbits-1:0] out_msg,
   output             out_val,
   input              out_rdy,
  );
    ...
  endmodule

A PyMTL Verilog wrapper using manually specified port names and inferred file,
module, and parameter names would look like the following::

  #============================================================================
  # PortBundleExVRTL.py
  #============================================================================
  # The PyMTL source file name matches the PyMTL class name, so name inference
  # can be used for the file name.

  from pymtl import *

  # The PyMTL wrapper class name matches the Verilog module name, so name
  # inference can be used for the module name.

  class PortBundleExVRTL( VerilogModel ):

    # The __init__ argument names match the Verilog module parameters, so name
    # inference be used for the parameters as well.

    def __init__( s, nbits = 1 ):
      s.in_ = InValRdyBundle ( nbits )
      s.out = OutValRdyBundle( nbits )

      # Name inference **does not** work on PortBundles, so below we manually
      # map the PyMTL Model ports to the port names of the Verilog module.

      s.set_ports({
        'in_msg':  s.in_.msg,
        'in_val':  s.in_.val,
        'in_rdy':  s.in_.rdy,
        'out_msg': s.out.msg,
        'out_val': s.out.val,
        'out_rdy': s.out.rdy,

        # The implicit PyMTL clk and reset ports must be explicitly connected.
        'clk'   :  s.clk,
        'reset' :  s.reset,
      })

-------------------------------------------------------------------------------
Creating a VerilogModel Wrapper Manually: A More Complex Example
-------------------------------------------------------------------------------

The previous example used a manual mapping for the module ports but name
inference for the file name, module name, and parameter names. In some cases,
the user may one to manually specify **all** of these configuration parameters
in their PyMTL Verilog wrapper.

Below is an alternate implementation of ``PortBundleExRTL.py`` that uses no
name inference and manually specifies the file, module, parameter, and port
names of the wrapper::

  #============================================================================
  # PortBundleExVRTL.py
  #============================================================================

  from pymtl import *

  class PortBundleExVRTL( VerilogModel ):

    # The Verilog module name is specified using the "modulename" attribute.
    modulename = 'PortBundleExVRTL'

    # The Verilog source file is specified using the "sourcefile" attribute.
    # Note that sourcefile must contain a fully qualified pathname.
    sourcefile = os.path.join( os.path.dirname(__file__),
                               'PortBundleExVRTL.v' )

    def __init__( s, nbits = 1 ):
      s.in_ = InValRdyBundle ( nbits )
      s.out = OutValRdyBundle( nbits )

      # The Verilog parameter name to PyMTL argument mapping is specified by
      # passing a dictionary to the set_params method.

      s.set_params({
        'nbits' : nbits,
      })

      # The Verilog port name to PyMTL port mapping is specified by passing a
      # dictionary to the set_ports method.

      s.set_ports({
        'clk'   :  s.clk,
        'reset' :  s.reset,
        'in_msg':  s.in_.msg,
        'in_val':  s.in_.val,
        'in_rdy':  s.in_.rdy,
        'out_msg': s.out.msg,
        'out_val': s.out.val,
        'out_rdy': s.out.rdy,
      })

