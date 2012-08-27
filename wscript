#! /usr/bin/env python

top = '.'
out = 'build'

def configure(ctx):
  print('→ configuring the project in ' + ctx.path.abspath())

#------------------------------------------------------------------------
# build: currently empty
#------------------------------------------------------------------------
# TODO: look into variants in wafbook, section 6.2.2
def build(bld):
  pass

#------------------------------------------------------------------------
# check: run python tests using py.test
#------------------------------------------------------------------------
def check(bld):
  dirs = ['pymtl',
          'pex_regincr',
          'pex_sorter',
          ]
  for d in dirs:
    bld(rule='py.test ../'+d, always=True)

from waflib.Build import BuildContext
class check_class(BuildContext):
  cmd = 'check'
  fun = 'check'

#------------------------------------------------------------------------
# check_vc: build and run iverilog unit tests
#------------------------------------------------------------------------
# TODO: fix so that ./waf list and ./waf --targets=... works with this
def check_vc(bld):
  cmd = ("iverilog -DIVERILOG -DCLOCK_PERIOD=10 -g2005 -Wall "
         "-Wno-sensitivity-entire-vector -Wno-sensitivity-entire-array")

  #libs = bld.path.ant_glob('vc', dir=True)
  libs = '-I ' + bld.path.find_dir('vc').path_from(bld.bldnode)

  # Compile all test files
  test_files = bld.path.ant_glob('vc/*.t.v')

  # TODO: read about name and extension-based file processing in wafbook
  #       sections 8.2, 8.2.1
  for test in test_files:
    tgt = str(test).replace('.t.v', '-utst')
    bld(rule=cmd+' -o ${TGT} '+libs+' ${SRC}', source=test, target=tgt)
    bld(rule='./${SRC}', source=tgt)

from waflib.Build import BuildContext
class check_vc_class(BuildContext):
  cmd = 'check_vc'
  fun = 'check_vc'


#------------------------------------------------------------------------
# creating new command names build_debug and build_release
#------------------------------------------------------------------------
#from waflib.Build import BuildContext, CleanContext
#from waflib.Build import InstallContext, UninstallContext
#
#for x in 'debug release'.split():
#  for y in (BuildContext, CleanContext, InstallContext, UninstallContext):
#    name = y.__name__.replace('Context','').lower()
#      class tmp(y):
#        cmd = name + '_' + x
#        variant = x
