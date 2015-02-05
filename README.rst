===============================================================================
|PyMTL|
===============================================================================

|status|

PyMTL is an open-source, Python-based framework for multi-level hardware
modeling. It was recently introduced to the world at MICRO-47 in December,
2014.

Please note that PyMTL is currently **alpha** software that is under active
development and documentation is currently quite sparse. Please stay tuned
as we will be adding much more documentation and a tutorial over the next
several weeks.

Thank you for your interest!

.. |PyMTL| image:: docs/pymtl_logo.png

.. |status| image:: https://travis-ci.org/cornell-brg/pymtl.svg?branch=master
  :target: https://travis-ci.org/cornell-brg/pymtl

-------------------------------------------------------------------------------
License
-------------------------------------------------------------------------------

PyMTL is offered under the terms of the Open Source Initiative BSD 3-Clause
License. More information about this license can be found here:

- http://choosealicense.com/licenses/bsd-3-clause
- http://opensource.org/licenses/BSD-3-Clause

-------------------------------------------------------------------------------
Publications
-------------------------------------------------------------------------------

If you use PyMTL in your research, please cite our paper_! ::

  @article{lockhart-pymtl-micro2014,
    title     = {PyMTL: A Unified Framework for Vertically Integrated
                 Computer Architecture Research},
    author    = {Derek Lockhart and Gary Zibrat and Christopher Batten},
    journal   = {47th ACM/IEEE Int'l Symp. on Microarchitecture (MICRO-47)},
    month     = {Dec},
    year      = {2014},
  }

.. _paper: http://dx.doi.org/10.1109/MICRO.2014.50

-------------------------------------------------------------------------------
Installation
-------------------------------------------------------------------------------

Prerequisites
-------------

- Python2.7
- virtualenv
- libffi
- iverilog                      (for testing generated Verilog HDL)
- verilator                     (for testing generated Verilog HDL)
- PARC cross-compiler toolchain (for testing PARC processor model)

Installation
------------

We recommend using virtualenv to install PyMTL. To create a new virtualenv and
activate it, run::

  % mkdir ~/venvs
  % virtualenv --python=python2.7 ~/venvs/pymtl
  % source ~/venvs/pymtl/bin/activate

Checkout the PyMTL repository from GitHub and put it somewhere sane::

  % mkdir -p ~/vc/github-brg
  % cd ~/vc/github-brg
  % git clone https://github.com/cornell-brg/pymtl.git

Finally, use pip to install PyMTL in editable mode::

  % pip install --editable ./pymtl

Testing
-------

Before running any tests, we first create a build directory inside the PyMTL
repo to hold any temporary files generated during simulation::

  % mkdir -p ~/vc/pymtl/build
  % cd pymtl/build

All Python simulation tests can be easily run using py.test (warning: there are
a lot of tests!)::

  % py.test .. --verbose --tb=line

The Verilog simulation tests are only executed if the --test-verilog flag
is provided. For Verilog testing to work, PyMTL requires that Verilator is
on your PATH and that the PYMTL_VERILATOR_INCLUDE_DIR environment is
defined::

  % export PATH={path_to_verilator_binary}:$PATH
  % export PYMTL_VERILATOR_INCLUDE_DIR={path_to_verilator_include_directory}
  % py.test .. --verbose --test-verilog

When you're done testing/developing, you can deactivate the virtualenv::

  % deactivate

-------------------------------------------------------------------------------
Installing Verilator
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

  % cd ~/vc/github-brg/pymtl/build
  % py.test .. --verbose --test-verilog

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
- examples:   Simple Example PyMTL Models
- proc:       Processor Models
- mem:        Memory and Cache Models
- net:        On-Chip Network Models
- labs:       Course Labs
- tests:      PARC ISA Assembly Tests
- ubmark:     PARC ISA Microbenchmarks
- scripts:    Various scripts

To run the tests for a specific model, you can provide py.test with a path. The
verbose flag will explicitly list test names so you can see what fails::

  % py.test ../lab/imul --verbose

You should notice all the tests that run are passing, but there are two errors.
These errors are because there are no implementations for IntMulIterFixedLat
and IntMulIterVarLat provided.

To see detailed output from a specific test, use the -k flag to select the test
and the -s flag to dump the output.  The following command should output a
linetrace of the test_small_pp test::

  % py.test ../new_imul --verbose -k test_small_pp -s

