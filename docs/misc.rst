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
  % py.test ../proc/parc

To compile the PARC processor microbenchmarks::

  % mkdir -p ubmark/build
  % cd ubmark/build
  % ../configure --host=maven
  % make

To run the microbenchmarks::

  % cd ../../build
  % ??? # TODO

