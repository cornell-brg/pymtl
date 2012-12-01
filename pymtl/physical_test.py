#=========================================================================
# Register File
#=========================================================================

from pymtl import *
import pmlib

import math

#-------------------------------------------------------------------------
# Register
#-------------------------------------------------------------------------

class Reg( Model ):

  @capture_args
  def __init__( self, nbits = 1 ):
    self.in_ = InPort  ( nbits )
    self.out = OutPort ( nbits )

  @posedge_clk
  def seq_logic( self ):
    self.out.next = self.in_.value

  def physical_elaboration( self ):
    self._dim.h = 10
    self._dim.w = 5 * self.out.width

#-------------------------------------------------------------------------
# RegisterFile using Register Cells
#-------------------------------------------------------------------------

class RegisterFile( Model ):

  def __init__( self, nbits = 32, nregs = 32, rd_ports = 1 ):

    self.rd_ports = rd_ports
    self.nregs    = nregs
    addr_bits     = int( math.ceil( math.log( nregs, 2 ) ) )

    self.rd_addr  = [ InPort( addr_bits ) for x in xrange(rd_ports) ]
    self.rd_data  = [ OutPort( nbits )    for x in xrange(rd_ports) ]
    self.wr_addr  = InPort( addr_bits )
    self.wr_data  = InPort( nbits )
    self.wr_en    = InPort( 1 )

    self.regs     = [ Reg( nbits ) for x in xrange( nregs ) ]

  @combinational
  def comb_logic( self ):
    for i in xrange( self.rd_ports ):
      addr = self.rd_addr[i].value.uint
      assert addr < self.nregs
      self.rd_data[i].value = self.regs[ addr ].out.value

    if self.wr_en.value:
      addr = self.wr_addr.value.uint
      assert addr < self.nregs
      self.regs[ addr ].in_.value = self.wr_data.value

  #  self.regs     = [ Wire( nbits ) for x in xrange( nregs ) ]

  #@combinational
  #def comb_logic( self ):
  #  for i in xrange( self.rd_ports ):
  #    # TODO: complains if no uint, list indices must be integers.
  #    #       How do we make this translatable?
  #    addr = self.rd_addr[i].value.uint
  #    assert addr < self.nregs
  #    self.rd_data[i].value = self.regs[ addr ].value

  #@posedge_clk
  #def seq_logic( self ):
  #  if self.wr_en.value:
  #    addr = self.wr_addr.value.uint
  #    assert addr < self.nregs
  #    # TODO: will this translate and synthesize to what we want?
  #    #       Or does the read need to have this check?
  #    self.regs[ addr ].next = self.wr_data.value

  def line_trace( self ):
    return [x.out.value.uint for x in self.regs]

  def physical_elaboration( self ):

    for reg in self.get_submodules():
      # Elaborate the children
      reg.physical_elaboration()

      # Offset the child origin, running sum
      reg._dim.y   = self._dim.h
      self._dim.h += reg._dim.h
      self._dim.w  = reg._dim.w


#-------------------------------------------------------------------------
# Physical Test
#-------------------------------------------------------------------------

def test_physical_elaboration():
  model = RegisterFile()
  model.elaborate()
  model.physical_elaboration()
  print
  model.dump_physical_design()

#-------------------------------------------------------------------------
# Simulation Test
#-------------------------------------------------------------------------

def test_regfile_1R1W( dump_vcd ):

  # Test vectors

  test_vectors = [
    # rd_addr0  rd_data0  wr_en  wr_addr  wr_data
    [       0,   0x0000,     0,       0,   0x0000 ],
    [       1,   0x0000,     0,       1,   0x0008 ],
    # Write followed by Read
    [       3,   0x0000,     1,       2,   0x0005 ],
    [       2,   0x0005,     0,       2,   0x0000 ],
    # Simultaneous Write and Read
    [       3,   0x0000,     1,       3,   0x0007 ],
    [       3,   0x0007,     1,       7,   0x0090 ],
    [       7,   0x0090,     1,       3,   0x0007 ],
    # Write to zero
    [       0,   0x0000,     1,       0,   0x0FFF ],
    [       0,   0x0FFF,     1,       4,   0x0FFF ],
    [       0,   0x0FFF,     0,       4,   0x0BBB ],
    [       0,   0x0FFF,     0,       4,   0x0FFF ],
    [       4,   0x0FFF,     0,       0,   0x0000 ],
  ]

  # Instantiate and elaborate the model

  model = RegisterFile( nbits=16, nregs=8, rd_ports=1 )
  model.elaborate()

  # Define functions mapping the test vector to ports in model

  def tv_in( model, test_vector ):
    model.rd_addr[0].value = test_vector[0]
    model.wr_en.value      = test_vector[2]
    model.wr_addr.value    = test_vector[3]
    model.wr_data.value    = test_vector[4]

  def tv_out( model, test_vector ):
    #if test_vector[3] != '?':
    assert model.rd_data[0].value == test_vector[1]

  # Run the test

  sim = pmlib.TestVectorSimulator( model, test_vectors, tv_in, tv_out )
  if dump_vcd:
    sim.dump_vcd( "plab2-test_regfile_1R1W.vcd" )
  sim.run_test()
