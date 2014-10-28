#=======================================================================
# IntMulDivCL.py
#=======================================================================

from pymtl    import *
from new_pmlib    import InValRdyBundle, OutValRdyBundle
from IntDivIterCL import IntDivIterCL
from new_imul     import IntMulIterVarLat
from muldiv_msg   import BitStructIndex

import new_pmlib

#-----------------------------------------------------------------------
# IntMulDivCL
#-----------------------------------------------------------------------
class IntMulDivCL( Model ):

  # Constants
  idx = BitStructIndex()

  #---------------------------------------------------------------------
  # __init__
  #---------------------------------------------------------------------
  def __init__( s ):

    s.in_ = InValRdyBundle ( s.idx.length )
    s.out = OutValRdyBundle( 32 )

  #---------------------------------------------------------------------
  # elaborate_logic
  #---------------------------------------------------------------------
  def elaborate_logic( s ):

    s.in_op  = Wire( 1 )  # determines mul/div
    s.op     = Wire( 1 )

    s.intMul = IntMulIterVarLat()
    s.intDiv = IntDivIterCL()

    @s.combinational
    def comblogic():

      s.intMul.in_.msg.value = s.in_.msg
      s.intDiv.in_.msg.value = s.in_.msg
      s.intMul.out.rdy.value = s.out.rdy
      s.intDiv.out.rdy.value = s.out.rdy

      s.in_.rdy.value = s.intDiv.in_.rdy and s.intMul.in_.rdy
      s.out.val.value = s.intDiv.out.val or  s.intMul.out.val

      s.intMul.in_.val.value = s.in_.val and s.in_.rdy and \
                               s.in_.msg[s.idx.muldiv_op] == s.idx.MUL_OP

      s.intDiv.in_.val.value = s.in_.val and s.in_.rdy and \
                             ( s.in_.msg[s.idx.muldiv_op] == s.idx.DIV_OP  or
                               s.in_.msg[s.idx.muldiv_op] == s.idx.REM_OP  or
                               s.in_.msg[s.idx.muldiv_op] == s.idx.DIVU_OP or
                               s.in_.msg[s.idx.muldiv_op] == s.idx.REMU_OP )

      if   (s.intMul.out.val == 1): s.out.msg.value = s.intMul.out.msg
      elif (s.intDiv.out.val == 1): s.out.msg.value = s.intDiv.out.msg
      else:                         s.out.msg.value = 0

  #---------------------------------------------------------------------
  # line_trace
  #---------------------------------------------------------------------
  def line_trace( s ):

    return "|{} () {}".format( s.in_, s.out )

    #if (s.in_.msg[s.idx.muldiv_op] == s.idx.MUL_OP):
    #  op= "mul "
    #if (s.in_.msg[s.idx.muldiv_op] == s.idx.DIV_OP):
    #  op= "div "
    #if (s.in_.msg[s.idx.muldiv_op] == s.idx.REM_OP):
    #  op= "rem "
    #if (s.in_.msg[s.idx.muldiv_op] == s.idx.DIVU_OP):
    #  op= "divu"
    #if (s.in_.msg[s.idx.muldiv_op] == s.idx.REMU_OP):
    #  op= "remu"

    #return "{} sri={} svi={} sro={} svo={} mri={} mvi={} mro={} mvo={} dri={} dvi={} dro={} dvo={} mout{}" \
    #    .format( op, s.in_.rdy , s.in_.val , s.out.rdy , s.out.val , \
    #    s.intMul.in_.rdy , s.intMul.in_.val , s.intMul.out.rdy , s.intMul.out.val , \
    #    s.intDiv.in_.rdy , s.intDiv.in_.val ,  s.intDiv.out.rdy , s.intDiv.out.val , \
    #    s.intMul.out.msg         )

