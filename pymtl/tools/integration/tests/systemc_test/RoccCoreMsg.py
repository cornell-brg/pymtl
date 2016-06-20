# -*- coding: utf-8 -*-

#=========================================================================
# RoccCoreMsg
#=========================================================================
# PyMTL implementation of the register mode signals (prefixed with Core)
# of The Rocket Custom Coprocessor interface (ROCC)
#
# The Register mode signals are composed of the RoCC Command and Response
# subgroups. All the signal names are prefixed with “core” to denote
# their source.

from pymtl import *

#-------------------------------------------------------------------------
# RoccCoreCmdMsg
#-------------------------------------------------------------------------
# Core command messages.
#
# Signal names in the list below are used in Rocket chip. They are prefixed
# with core_cmd_ to indicate signal group and suffixed with _i to indicate
# their direction is from the core to accelerators.
#
# Width   Signal name                 Default value   Description
#
#     7   core_cmd_inst_funct_i              funct7   Accelerator instructions
#     5   core_cmd_inst_rs2_i                   rs2   Source register IDs
#     5   core_cmd_inst_rs1_i                   rs1   "
#     1   core_cmd_inst_xd_i                     xd   Set if rd exists
#     1   core_cmd_inst_xs1_i                   xs1   Set if rs exitsts
#     1   core_cmd_inst_xs2_i                   xs2   "
#     5   core_cmd_inst_rd_i                     rd   Destination register ID
#     7   core_cmd_inst_opcode_i    0x1/0x2/0x3/0x4   Custom instruction opcode
#    64   core_cmd_rs1_i                   rs1_data   Source register data
#    64   core_cmd_rs2_i                   rs2_data   Source register data
#
# Those signals are arranged in a message format:
#
#        7b          5b         5b         1b        1b         1b         5b         7b        64b   64b
#  +------------+----------+----------+---------+----------+----------+---------+-------------+-----+-----+
#  | inst_funct | inst_rs2 | inst_rs1 | inst_xd | inst_xs1 | inst_xs2 | inst_rd | inst_opcode | rs1 | rs2 |
#  +------------+----------+----------+---------+----------+----------+---------+-------------+-----+-----+
#

class RoccCoreCmdMsg( BitStructDefinition ):

  def __init__( s ):
    s.inst_funct  = BitField( 7  )
    s.inst_rs2    = BitField( 5  )
    s.inst_rs1    = BitField( 5  )
    s.inst_xd     = BitField( 1  )
    s.inst_xs1    = BitField( 1  )
    s.inst_xs2    = BitField( 1  )
    s.inst_rd     = BitField( 5  )
    s.inst_opcode = BitField( 7  )
    s.rs1         = BitField( 64 )
    s.rs2         = BitField( 64 )

  def __str__( s ):
    return "cmd:{}:{}".format( s.rs1, s.rs2 )

#-------------------------------------------------------------------------
# RoccCoreRespMsg
#-------------------------------------------------------------------------
# Core command messages.
#
# Signal names in the list below are used in Rocket chip. They are prefixed
# with core_cmd_ to indicate signal group and suffixed with _i to indicate
# their direction is from the core to accelerators.
#
# Width   Signal name        Default value   Description
#
#     7   core_resp_rd_o               rd    Destination register ID in the response
#    64   core_resp_data_o        rd_data    Destination register data in the response
#
# Those signals are arranged in a message format:
#
#      5b         64b
#  +---------+-----------+
#  | resp_rd | resp_data |
#  +---------+-----------+
#

class RoccCoreRespMsg( BitStructDefinition ):

  def __init__( s ):
    s.resp_rd   = BitField( 5  )
    s.resp_data = BitField( 64 )

  def __str__( s ):
    return "resp:{}:{}".format( s.resp_rd, s.resp_data )
