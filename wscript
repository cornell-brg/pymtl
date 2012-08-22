#! /usr/bin/env python

top = '.'
out = 'build_out'

def configure(ctx):
  print('→ configuring the project in ' + ctx.path.abspath())

def build(ctx):
  tests = ['pymtl/simulate_test.py',
           'pymtl/translate_test.py',
           'pymtl/visualize.py',
           'pymtl/gcd_test.py',
           #'pymtl/vcd.t.py',
          ]

  for test in tests:
    ctx(rule='python ${SRC} --verbose', source=test)

