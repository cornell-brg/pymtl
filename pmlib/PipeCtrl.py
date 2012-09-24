#=========================================================================
# PipeCtrl
#=========================================================================
# This class models the pipeline squash and stall control signals for a
# given pipeline stage. A state element in the model represents the valid
# bit of the pipeline stage.
#
# Inputs:
# -------
#
# pvalid  : Valid bit coming from the previous stage in the pipeline
# nstall  : Stall signal originating from the next stage in the pipeline
# nsquash : Squash signal originating from the next stage in the pipeline
# ostall  : Stall signal originating from the current pipeline stage
# osquash : Squash signal originating from the current pipeline stage
#
# Outputs:
# --------
#
# nvalid      : Valid bit calculation for the next stage
# pstall      : Aggregate stall signal for the previous stage
# psquash     : Aggregate squash signal for the previous stage
# pipereg_en  : Enable Signal for all the pipeline registers at the begining
#               of current pipeline stage
# pipereg_val : Combinational valid bit value of the current stage
# pipe_go     : Go signal to perform the current pipeline stage transaction

from pymtl import *

import pmlib

class PipeCtrl (Model):

  def __init__( self ):

    #---------------------------------------------------------------------
    # Input  Ports
    #---------------------------------------------------------------------

    self.pvalid      = InPort ( 1 )
    self.nstall      = InPort ( 1 )
    self.nsquash     = InPort ( 1 )
    self.ostall      = InPort ( 1 )
    self.osquash     = InPort ( 1 )

    #---------------------------------------------------------------------
    # Output Ports
    #---------------------------------------------------------------------

    self.nvalid      = OutPort ( 1 )
    self.pstall      = OutPort ( 1 )
    self.psquash     = OutPort ( 1 )
    self.pipereg_en  = OutPort ( 1 )
    self.pipereg_val = OutPort ( 1 )
    self.pipe_go     = OutPort ( 1 )

    #---------------------------------------------------------------------
    # Static Elaboration
    #---------------------------------------------------------------------

    # current pipeline stage valid bit register

    self.val_reg = pmlib.regs.RegEn( 1 )

    connect( self.val_reg.in_, self.pvalid )

    # combinationally read out the valid bit of the current state and
    # assign it to pipereg_val

    connect( self.val_reg.out, self.pipereg_val )

  #-----------------------------------------------------------------------
  # Combinational Logic
  #-----------------------------------------------------------------------

  @combinational
  def comb( self ):

    # Insert microarchitectural 'nop' value when the current stage is
    # squashed due to nsquash or when the current stage is stalled due to
    # ostall or when the current stage is stalled due to nstall. Otherwise
    # pipeline the valid bit

    if self.nsquash.value or self.nstall.value or self.ostall.value:
      self.nvalid.value = 0
    else:
      self.nvalid.value = self.val_reg.out.value

    # Enable the pipeline registers when the current stage is squashed due
    # to nsquash or when the current stage is not stalling due to the
    # ostall or nstall. Otherwise do not set the enable signal

    if self.nsquash.value or not ( self.nstall.value or self.ostall.value ):
      self.pipereg_en.value = 1
      self.val_reg.en.value = 1
    else:
      self.pipereg_en.value = 0
      self.val_reg.en.value = 0

    # Set pipego when the current stage is not squashed and not stalled and
    # if the valid bit is set. Else a pipeline transaction will not occur.

    if ( self.val_reg.out.value and not self.nsquash.value
         and not self.nstall.value and not self.ostall.value ):
      self.pipe_go.value = 1
    else:
      self.pipe_go.value = 0

    # Accumulate stall signals

    self.pstall.value  = self.nstall.value  | self.ostall.value

    # Accumulate squash signals

    self.psquash.value = self.nsquash.value | self.osquash.value
