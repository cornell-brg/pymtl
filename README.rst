===============================================================================
PyMTL Installation
===============================================================================

.. image:: https://magnum.travis-ci.com/dmlockhart/pymtl.svg?token=jmi7kf1Uw55Qs4NmDdN1&branch=master
  :target: https://magnum.travis-ci.com/dmlockhart/pymtl

-------------------------------------------------------------------------------
Prerequisites
-------------------------------------------------------------------------------

 - Python2.7
 - virtualenv
 - iverilog                      (for testing generated Verilog HDL)
 - verilator                     (for testing generated Verilog HDL)
 - PARC cross-compiler toolchain (for testing PARC processor model)

-------------------------------------------------------------------------------
BRG Server Setup
-------------------------------------------------------------------------------

When running/developing PyMTL on the BRG servers, you should first run the
setup script. See the OSX/Linux section below for all other installation steps.

::

  % source setup-brg.sh

-------------------------------------------------------------------------------
OSX/Linux Installation
-------------------------------------------------------------------------------

Create a new Python virtualenv and activate it::

  % mkdir ~/venvs
  % virtualenv --python=python2.7 ~/venvs/pymtl
  % source ~/venvs/pymtl/bin/activate

Install Python package prerequisites using pip::

  % pip install yolk pytest pytest-xdist cffi greenlets
  % yolk -l

Checkout the repo::

  % mkdir -p ~/vc/github-brg
  % cd ~/vc/github-brg
  % git clone git@github.com:cornell-brg/pymtl.git
  % cd pymtl

Create a build directory and run the tests::

  % mkdir build
  % cd build
  % py.test .. --tb=line

When you're done testing/developing, you can disable the virtualenv::

  % deactivate

-------------------------------------------------------------------------------
Model Development
-------------------------------------------------------------------------------

The first thing you should do anytime you plan on working with PyMTL is change
to the repository build directory and activate the virtualenv::

  % cd ~/vc/github-brg/pymtl
  % source ~/venvs/2.7/bin/activate

The top-level repo directory should have the following layout:

  - pymtl:      PyMTL Core Model Library and Tools
  - pclib:      PyMTL Component Library
  - new_gcd:    Greatest Common Divisor Models
  - new_imul:   Iterative Multiplier Models
  - new_mesh:   Mesh Network Models
  - new_mem:    Direct Mapped Cache Models
  - new_proc:   PARC Processor Models
  - tests:      PARC ISA Assembly Tests
  - ubmark:     PARC ISA Microbenchmarks
  - scripts:    Various scripts

To run the tests for a specific model, you can provide py.test with a path. The
verbose flag will explicitly list test names so you can see what fails::

  % py.test ../new_imul --verbose

You should notice all the tests that run are passing, but there are two errors.
These errors are because there are no implementations for IntMulIterFixedLat
and IntMulIterVarLat provided.

To see detailed output from a specific test, use the -k flag to select the test
and the -s flag to dump the output.  The following command should output a
linetrace of the test_small_pp test::

  % py.test ../new_imul --verbose -k test_small_pp -s

-------------------------------------------------------------------------------
Running Verilog Tests
-------------------------------------------------------------------------------

The verilog tests require that the verilator toolchain is installed::

  % mkdir -p ~/vc/git-opensource
  % cd ~/vc/git-opensource
  % git clone http://git.veripool.org/git/verilator
  % cd verilator

Build the configure script, configure to build in place, then make the
verilator binary::

  % autoconf
  % export VERILATOR_ROOT=`pwd`
  % ./configure
  % make

Return to the PyMTL build directory and run the tests::

  % cd ~/vc/git-brg/parc/build
  % py.test .. --verbose --test-verilog

-------------------------------------------------------------------------------
Running Processor Tests
-------------------------------------------------------------------------------

The majority of the processor tests require the use of binaries compiled using
the PARC cross-compiler toolchain. This toolchain is already installed on the
BRG servers an can be accessed by sourcing the brg setup script::

  % source setup-brg.sh

To install the cross-compiler toolchain on a personal machine, please see the
documentation provided by the toolchain.

To compile the PARC processor assembly tests::

  % mkdir -p tests/build
  % cd tests/build
  % ../configure --host=maven
  % make

To run the tests::

  % cd ../../build
  % py.test ../new_proc

To compile the PARC processor microbenchmarks::

  % mkdir -p ubmark/build
  % cd ubmark/build
  % ../configure --host=maven
  % make

To run the microbenchmarks::

  % cd ../../build
  % ??? # TODO

