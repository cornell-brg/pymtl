#! /usr/bin/env python

import os

cmds = [

  #************************************
  # Run Assembly Tests
  #************************************

  # Single core baseline
  'make check-asm-pv2byp',
  'make check-asm-rand-pv2byp',

  # Compositions
  'make check-asm-pc',
  'make check-asm-pn',

  # Quad-core processor
  'make check-asm-pnc',

  #************************************
  # Run Benchmarks
  #************************************

  # Check Benchmarks
  'make run-bmark-pv2byp',
  'make run-bmark-pc',
  'make run-bmark-pn',
  'make run-bmark-pnc',

  #************************************
  # Run Traces
  #************************************

  'make run-traces-pcache',
  'make run-traces-pnet',
]

# Creating Assembly Tests
#
#   cd ../tests/
#   mkdir build
#   cd build
#   ../configure --host=maven
#   make
#   ../convert
#   make
#   ../convert-cache

# Building Benchmarks
#
#   cd ../ubmark/
#   mkdir build
#   cd build
#   ../configure --host=maven
#   make
#   ../convert
#   make
#   ../convert-cache

# Creating Traces
#
#   cd ../traces/
#   mkdir build-pcache
#   cd build
#   ../convert-pcache
#   cd ..
#   mkdir build-pnet
#   cd build
#   ../convert-pnet

# Run all the tests!
for cmd in cmds:
  os.system(cmd)
