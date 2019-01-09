 ![PyMTL](docs/pymtl_logo.png)
==========================================================================

[![Build Status](https://travis-ci.org/cornell-brg/pymtl.svg?branch=master)](https://travis-ci.org/cornell-brg/pymtl)

PyMTL is an open-source, Python-based framework for multi-level hardware
modeling. It was introduced at MICRO-47 in December, 2014. Please note
that PyMTL is currently **alpha** software that is under active
development and documentation is currently quite sparse. We have recently
received funding from the National Science Foundation under [Award #1512937][1]
to improve PyMTL performance, documentation, and reference models. Please
stay tuned over the next few months.

 [1]: http://www.nsf.gov/awardsearch/showAward?AWD_ID=1512937

Tutorials
--------------------------------------------------------------------------

If you are interested in learning more about the PyMTL framework, we
recommend you take a look at two tutorials that have been developed for
Cornell ECE 4750. This is a course on computer architecture targeting
seniors and first-year graduate students. Throughout the semester,
students gradually design, implement, test, and evaluate a basic
multicore system capable of running simple parallel applications at the
register-transfer level. This year, students are using the PyMTL
framework for all functional-level modeling and testing. Students have
the option of using PyMTL or Verilog for the RTL design portion of the
lab assignments. The first tutorial focuses on the PyMTL framework, while
the second tutorial illustrates how PyMTL's Verilog import feature can
enable applying PyMTL's powerful functional-level and testing features to
RTL designs written in Verilog.

 - [PyMTL Hardware Modeling Framework Tutorial](http://www.csl.cornell.edu/courses/ece4750/handouts/ece4750-tut3-pymtl.pdf)
   ([github](https://github.com/cornell-ece4750/ece4750-tut3-pymtl))
 - [Verilog Hardware Description Language Tutorial](http://www.csl.cornell.edu/courses/ece4750/handouts/ece4750-tut4-verilog.pdf)
   ([github](https://github.com/cornell-ece4750/ece4750-tut4-verilog))

We have also developed tutorials specifically on PyMTL CL modeling,
integrating PyMTL with the Xilinx Vivado High-Level Synthesis (HLS) tool,
and using PyMTL to drive a Synopys-based ASIC EDA toolflow.

 - [PyMTL CL Modeling Tutorial](https://github.com/cornell-ece5745/ece5745-sec-pymtl-cl/blob/master/README.md)
   ([github](https://github.com/cornell-ece5745/ece5745-sec-pymtl-cl))
 - [PyMTL/HLS Tutorial](https://github.com/cornell-brg/pymtl-tut-hls/blob/master/README.md)
   ([github](https://github.com/cornell-brg/pymtl-tut-hls))
 - [PyMTL-Based ASIC Toolflow Tutorial](http://www.csl.cornell.edu/courses/ece5745/handouts/ece5745-tut-asic-new.pdf)

License
--------------------------------------------------------------------------

PyMTL is offered under the terms of the Open Source Initiative BSD
3-Clause License. More information about this license can be found here:

 - http://choosealicense.com/licenses/bsd-3-clause
 - http://opensource.org/licenses/BSD-3-Clause

Publications
--------------------------------------------------------------------------

If you use PyMTL in your research, please cite our [MICRO'14 paper][3]:

```
  @inproceedings{lockhart-pymtl-micro2014,
    title     = {PyMTL: A Unified Framework for Vertically Integrated
                 Computer Architecture Research},
    author    = {Derek Lockhart and Gary Zibrat and Christopher Batten},
    booktitle = {47th IEEE/ACM Int'l Symp. on Microarchitecture (MICRO)},
    month     = {Dec},
    year      = {2014},
    pages     = {280--292},
    doi       = {10.1109/MICRO.2014.50},
  }
```

 [3]: http://dx.doi.org/10.1109/MICRO.2014.50

Installation
--------------------------------------------------------------------------

PyMTL requires Python2.7 and has the following additional prerequisites:

 - verilator, pkg-config
 - git, Python headers, and libffi
 - virtualenv

The steps for installing these prerequisites and PyMTL on a fresh Ubuntu
distribution are shown below. They have been tested with Ubuntu Trusty
14.04.

### Install Verilator

[Verilator][4] is an open-source toolchain for compiling Verilog RTL
models into C++ simulators. PyMTL uses Verilator for both Verilog
translation and Verilog import. You can install Verilator using the
standard package manager but the version available in the package
repositories is several years old. This means you will need to build and
install Verilator from source using the following commands:

```
 % sudo apt-get install git make autoconf g++ flex bison
 % mkdir -p ${HOME}/src
 % cd ${HOME}/src
 % wget http://www.veripool.org/ftp/verilator-3.876.tgz
 % tar -xzvf verilator-3.876.tgz
 % cd verilator-3.876
 % ./configure
 % make
 % sudo make install
```

You may need to install `flex-old` instead of `flex` on newer Linux
distributions. Verify that Verilator is on your path as follows:

```
 % cd $HOME
 % which verilator
 % verilator --version
```

PyMTL uses `pkg-config` to find the Verilator source files when
performing both Verilog translation and Verilog import. Install
`pkg-config` and verify that it is setup correctly as follows:

```
 % sudo apt-get install pkg-config
 % pkg-config --print-variables verilator
```

If `pkg-config` cannot find information about verilator, then you can
also explicitly set the following special environment variable:

```
 % export PYMTL_VERILATOR_INCLUDE_DIR="/usr/local/share/verilator/include"
```

 [4]: http://www.veripool.org/wiki/verilator

### Install git, Python headers, and libffi

We need to install the Python headers and libffi in order to be able to
install the cffi Python package. cffi provides an elegant way to call C
functions from Python, and PyMTL uses cffi to call C code generated by
Verilator. We will use git to grab the PyMTL source. The following
commands will install the appropriate packages:

```
 % sudo apt-get install git python-dev libffi-dev
```

### Install virtualenv

While not strictly necessary, we strongly recommend using [virtualenv][5]
to install PyMTL and the Python packages that PyMTL depends on.
virtualenv enables creating isolated Python environments. The following
commands will install virtualenv:

```
 % sudo apt-get install python-virtualenv
```

Now we can use the `virtualenv` command to create a new virtual
environment for PyMTL, and then we can use the corresponding `activate`
script to activate the new virtual environment:

```
 % mkdir ${HOME}/venvs
 % virtualenv --python=python2.7 ${HOME}/venvs/pymtl
 % source ${HOME}/venvs/pymtl/bin/activate
```

 [5]: https://virtualenv.pypa.io/en/latest/

### Install PyMTL

We can now use git to clone the PyMTL repo, and pip to install PyMTL and
its dependencies. Note that we use pip in editable mode so that we can
actively work in the PyMTL git repo.

```
 % mkdir -p ${HOME}/vc/git-hub/cornell-brg
 % cd ${HOME}/vc/git-hub/cornell-brg
 % git clone https://github.com/cornell-brg/pymtl.git
 % pip install --editable ./pymtl
 % pip install --upgrade 'pytest<=3.9.1'
```

Note that currently we require an older version of `py.test` but we are
working on upgrading PyMTL to use the most recent version.

Testing
--------------------------------------------------------------------------

Before running any tests, we first create a build directory inside the
PyMTL repo to hold any temporary files generated during simulation:

```
 % mkdir -p ${HOME}/vc/git-hub/cornell-brg/pymtl/build
 % cd ${HOME}/vc/git-hub/cornell-brg/pymtl/build
```

All Python simulation tests can be easily run using py.test (warning:
there are a lot of tests!):

```
 % py.test ..
```

The Verilog simulation tests are only executed if the `--test-verilog`
flag is provided. For Verilog testing to work, PyMTL requires that
Verilator is on your `PATH` and that the `PYMTL_VERILATOR_INCLUDE_DIR`
environment:

```
 % py.test .. --test-verilog
```

When you're done testing/developing, you can deactivate the virtualenv::

```
 % deactivate
```

