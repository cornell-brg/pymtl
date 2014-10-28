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

import pclib

class PipeCtrl (Model):

  def __init__( s ):

    #---------------------------------------------------------------------
    # Input  Ports
    #---------------------------------------------------------------------

    s.pvalid      = InPort ( 1 )
    s.nstall      = InPort ( 1 )
    s.nsquash     = InPort ( 1 )
    s.ostall      = InPort ( 1 )
    s.osquash     = InPort ( 1 )

    #---------------------------------------------------------------------
    # Output Ports
    #---------------------------------------------------------------------

    s.nvalid      = OutPort ( 1 )
    s.pstall      = OutPort ( 1 )
    s.psquash     = OutPort ( 1 )
    s.pipereg_en  = OutPort ( 1 )
    s.pipereg_val = OutPort ( 1 )
    s.pipe_go     = OutPort ( 1 )

  #---------------------------------------------------------------------
  # Static Elaboration
  #---------------------------------------------------------------------

  def elaborate_logic( s ):

    # current pipeline stage valid bit register

    s.val_reg = pclib.regs.RegEnRst( 1, reset_value = 0 )

    s.connect( s.val_reg.in_, s.pvalid )

    # combinationally read out the valid bit of the current state and
    # assign it to pipereg_val

    s.connect( s.val_reg.out, s.pipereg_val )

    #-----------------------------------------------------------------------
    # Combinational Logic
    #-----------------------------------------------------------------------

    @s.combinational
    def comb():

      # Insert microarchitectural 'nop' value when the current stage is
      # squashed due to nsquash or when the current stage is stalled due to
      # ostall or when the current stage is stalled due to nstall. Otherwise
      # pipeline the valid bit

      if s.nsquash.value or s.nstall.value or s.ostall.value:
        s.nvalid.value = 0
      else:
        s.nvalid.value = s.val_reg.out.value

      # Enable the pipeline registers when the current stage is squashed due
      # to nsquash or when the current stage is not stalling due to the
      # ostall or nstall. Otherwise do not set the enable signal

      if s.nsquash.value or not ( s.nstall.value or s.ostall.value ):
        s.pipereg_en.value = 1
        s.val_reg.en.value = 1
      else:
        s.pipereg_en.value = 0
        s.val_reg.en.value = 0

      # Set pipego when the current stage is not squashed and not stalled and
      # if the valid bit is set. Else a pipeline transaction will not occur.

      if ( s.val_reg.out.value and not s.nsquash.value
           and not s.nstall.value and not s.ostall.value ):
        s.pipe_go.value = 1
      else:
        s.pipe_go.value = 0

      # Accumulate stall signals

      s.pstall.value  = s.nstall.value  | s.ostall.value

      # Accumulate squash signals

      s.psquash.value = s.nsquash.value | s.osquash.value
