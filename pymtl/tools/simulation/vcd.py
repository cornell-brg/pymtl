#=======================================================================
# vcd.py
#=======================================================================
# VCD generation support for SimulationTool. VCD file format standard
# can be found here:
#
# - http://support.ema-eda.com/search/eslfiles/default/main/sl_legacy_releaseinfo/staging/sl3/release_info/psd142/vlogref/chap20.html#1031979
# - http://staff.ustc.edu.cn/~songch/download/IEEE.1364-2005.pdf
#
# TODO:
#
# - distinguish reg signals from wire signals (maybe)

from __future__ import print_function

import time
import sys

#-----------------------------------------------------------------------
# get_vcd_timescale
#-----------------------------------------------------------------------
DEFAULT_TIMESCALE = '10ps'
def get_vcd_timescale( model ):
  try:
    return model.vcd_timescale
  except AttributeError:
    return DEFAULT_TIMESCALE

#-----------------------------------------------------------------------
# write_vcd_header
#-----------------------------------------------------------------------
def write_vcd_header( o, model ):

  def dedent( lines, trim=4 ):
    return ''.join( [x[trim:]+'\n' for x in lines.split('\n')] ).lstrip()

  print( dedent("""
    $date
        {time}
    $end
    $version
        PyMTL ?.??
    $end
    $timescale
        {vcd_timescale}
    $end"""
    ).format(
      time          = time.asctime(),
      vcd_timescale = get_vcd_timescale( model ),
    ),
  file=o )

#-----------------------------------------------------------------------
# mangle_name
#-----------------------------------------------------------------------
# Mangle signal names so that lists of signals/models show up correctly.
def mangle_name( name ):
  return name.replace('[','(').replace(']',')')

#-----------------------------------------------------------------------
# write_vcd_signal_defs
#-----------------------------------------------------------------------
def write_vcd_signal_defs( o, model ):

  vcd_symbol = _gen_vcd_symbol()
  all_nets   = set()

  # Inner utility function to perform recursive descent of the model.
  def recurse_models( model, level ):

    # Create a new scope for this module
    print( "$scope module {name} $end".format( name=model.name ), file=o )

    # Define all signals for this model.
    for i in model.get_ports() + model.get_wires():

      # Multiple signals may be collapsed into a single net in the
      # simulator if they are connected. Generate new vcd symbols per
      # net, not per signal as an optimization.
      net = i._signalvalue
      if not hasattr( net, '_vcd_symbol' ):
        net._vcd_symbol = vcd_symbol.next()
        net._vcd_is_clk = i.name == 'clk'
      symbol = net._vcd_symbol

      print( "$var {type} {nbits} {symbol} {name} $end".format(
          type='reg', nbits=i.nbits, symbol=symbol, name=mangle_name(i.name),
      ), file=o )

      all_nets.add( net )

    # Recursively visit all submodels.
    for submodel in model.get_submodules():
      recurse_models( submodel, level+1 )

    print( "$upscope $end", file=o )

  # Begin recursive descent from the top-level model.
  recurse_models( model, 0 )

  # Once all models and their signals have been defined, end the
  # definition section of the vcd and print the initial values of all
  # nets in the design.
  print( "$enddefinitions $end\n", file=o )
  for net in all_nets:
    print( "b{value} {symbol}".format(
        value=net.bin(), symbol=net._vcd_symbol,
    ), file=o )

  return all_nets

#-----------------------------------------------------------------------
# insert_vcd_callbacks
#-----------------------------------------------------------------------
# Add callbacks which write the vcd file for each net in the design.
def insert_vcd_callbacks( sim, nets ):

  # A utility function which creates callbacks that write a nets current
  # value to the vcd file. The returned callback function is a closure
  # which is executed by the simulator whenever the net's value changes.
  def create_vcd_callback( sim, net ):

    # Each signal writes its binary value and unique identifier to the
    # specified vcd file
    if not net._vcd_is_clk:
      cb = lambda: print( 'b%s %s\n' % (net.bin(), net._vcd_symbol),
                          file=sim.vcd )

    # The clock signal additionally must update the vcd time stamp
    else:
      cb = lambda: print( '#%s\nb%s %s\n' % (100*sim.ncycles+50*net.uint(),
                          net.bin(), net._vcd_symbol),
                          file=sim.vcd )

    # Return the callback
    return cb

  # For each net in the simulator, create a callback and register it with
  # the net to be fired whenever the value changes. We repurpose the
  # existing callback facilities designed for slices (these execute
  # immediately), rather than the default callback mechanism (these are
  # put on the event queue to execute later).
  for net in nets:
    net.register_slice( create_vcd_callback( sim, net ) )

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

    # Write out vcd header, signal definitions, and initial state

    write_vcd_header( outfile, simulator.model )
    nets = write_vcd_signal_defs( outfile, simulator.model )

    # Enable vcd mode on the simulator, set simulator output file name

    simulator.vcd = outfile
    insert_vcd_callbacks( simulator, nets )
