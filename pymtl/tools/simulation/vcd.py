#=======================================================================
# vcd.py
#=======================================================================
# VCD generation support for SimulationTool. VCD file format standard
# can be found here:
#
# - http://support.ema-eda.com/search/eslfiles/default/main/sl_legacy_releaseinfo/staging/sl3/release_info/psd142/vlogref/chap20.html#1031979
# - http://staff.ustc.edu.cn/~songch/download/IEEE.1364-2005.pdf

import time
import sys

#-----------------------------------------------------------------------
# write_vcd_header
#-----------------------------------------------------------------------
def write_vcd_header( o ):

  def dedent( lines, trim=4 ):
    return ''.join( [x[trim:]+'\n' for x in lines.split('\n')] ).lstrip()

  print >> o, dedent("""
    $date
        {time}
    $end
    $version
        PyMTL ?.??
    $end
    $timescale
        1ns
    $end"""
  ).format( time=time.asctime() )

#-----------------------------------------------------------------------
# write_vcd_signal_defs
#-----------------------------------------------------------------------
def write_vcd_signal_defs( o, model ):

  vcd_symbol  = _gen_vcd_symbol()
  all_signals = []

  def recurse_models( model, level ):

    print >> o, "$scope module %s $end" % model.name

    for i in model.get_ports() + model.get_wires():
      symbol  = vcd_symbol.next()
      i._code = symbol
      print >> o, "$var {type} {nbits} {symbol} {name} $end".format(
          type='reg', nbits=i.nbits, symbol=symbol, name=i.name,
      )
      all_signals.append( i )

    for submodel in model.get_submodules():
      recurse_models( submodel, level+1 )

    print >> o, "$upscope $end"

  recurse_models( model, 0 )
  print >> o, "$enddefinitions $end\n"

  for i in all_signals:
    print >> o, "b{value} {symbol}".format(
        value=i._signalvalue.bin_str(), symbol=i._code,
    )


#-----------------------------------------------------------------------
# _gen_vcd_symbol
#-----------------------------------------------------------------------
# Utility generator to create new symbols for each VCD signal.
# Code inspired by MyHDL 0.7.
def _gen_vcd_symbol():

  # Generate a string containing all valid vcd symbol characters
  _codechars = ''.join([chr(i) for i in range(33, 127)])
  _mod       = len(_codechars)

  # Function to map an integer n to a new vcd symbol
  def next_vcd_symbol(n):
    q, r = divmod(n, _mod)
    code = _codechars[r]
    while q > 0:
      q, r = divmod(q, _mod)
      code = _codechars[r] + code
    return code

  # Generator logic
  n = 0
  while 1:
    yield next_vcd_symbol(n)
    n += 1


#-----------------------------------------------------------------------
# VCDUtil
#-----------------------------------------------------------------------
# Hidden class used by the simulator tool for generating VCD output.
# This class takes a SimulationTool instance and augments it to generate
# VCD output.
class VCDUtil():

  def __init__(self, simulator, outfile=None):

    # Select the output for VCD

    if not outfile:
      outfile = sys.stdout
    elif isinstance(outfile, str):
      outfile = open( outfile, 'w' )
    else:
      outfile = outfile

    # Write the simulator

    write_vcd_header     ( outfile )
    write_vcd_signal_defs( outfile, simulator.model )

    # Enable vcd mode on the simulator, set simulator output file name

    simulator.vcd = True
    simulator.o   = outfile
