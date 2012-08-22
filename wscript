#! /usr/bin/env python

top = '.'
out = 'build_out'

def configure(ctx):
  print('→ configuring the project in ' + ctx.path.abspath())

def options(ctx):
  ctx.add_option('--tgt', action='store', default=False)

def build(ctx):
  tests = ['pymtl/simulate.t.py',
           'pymtl/translate.t.py',
           'pymtl/visualize.py',
           'pymtl/gcd.t.py',
          ]

  if not ctx.options.tgt:
    for test in tests:
      ctx(rule='python ${SRC}', source=test)
  else:
    test = 'pymtl/{0}.t.py'.format( ctx.options.tgt )
    ctx(rule='python ${SRC}', source=test)


