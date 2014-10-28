#=========================================================================
# DirectedMappedWriteBackCacheTagArray
#=========================================================================
# Directed Mapped Cache Tag Array. Each entry in the Tag Array has a valid
# and dirty bit along with the tag contents. Tag Array is modeled using a
# method interfaces. Tag Array provides a search, write method which
# perform actions on the tag contents. It also provides validate /
# invalidate which operate on the valid bit and clean / dirty methods which
# operate on the dirty bit.

from   pymtl import *
import pclib

import math

from   SRAMs import SRAM1r1w
from   RAMs  import RAM_rst_1r1w

#-------------------------------------------------------------------------
# DirectMappedWriteBackCacheTagArrayCtrl
#-------------------------------------------------------------------------

class DirectMappedWriteBackCacheTagArrayCtrl (Model):

  def __init__( s, num_entries ):

    # address bits

    s.addr_nbits = int( math.ceil( math.log( num_entries, 2 ) ) )

    #---------------------------------------------------------------------
    # Interface Ports
    #---------------------------------------------------------------------

    # Search Method : enable search and tag search pointer

    s.search_do       = InPort  ( 1 )
    s.search_ptr      = InPort  ( s.addr_nbits )

    # Write Method : enable write and tag write pointer

    s.write_do        = InPort  ( 1 )
    s.write_ptr       = InPort  ( s.addr_nbits )

    # Validate Method : enable validate and pointer to validate tag entry

    s.validate_do     = InPort  ( 1 )
    s.validate_ptr    = InPort  ( s.addr_nbits )

    # Invalidate Method : enable invalidate and pointer to invalidate tag
    # entry

    s.invalidate_do   = InPort  ( 1 )
    s.invalidate_ptr  = InPort  ( s.addr_nbits )

    # Clean Method : enable clean and pointer to clean tag entry

    s.clean_do        = InPort  ( 1 )
    s.clean_ptr       = InPort  ( s.addr_nbits )

    # Dirty Method : enable dirty and pointer to dirty tag entry

    s.dirty_do        = InPort  ( 1 )
    s.dirty_ptr       = InPort  ( s.addr_nbits )

    # Control Signals (ctrl -> dpath)

    s.ctrl_tag_en     = OutPort ( 1 )
    s.ctrl_tag_wen    = OutPort ( 1 )
    s.ctrl_tag_ptr    = OutPort ( s.addr_nbits )

    s.ctrl_valid_wen  = OutPort ( 1 )
    s.ctrl_valid_next = OutPort ( 1 )
    s.ctrl_valid_ptr  = OutPort ( s.addr_nbits )

    s.ctrl_dirty_wen  = OutPort ( 1 )
    s.ctrl_dirty_next = OutPort ( 1 )
    s.ctrl_dirty_ptr  = OutPort ( s.addr_nbits )

  def elaborate_logic( s ):

    # Temporary Wires

    s.tag_sel        = Wire ( 2 )

    s.connect( s.tag_sel[0],      s.search_do     )
    s.connect( s.tag_sel[1],      s.write_do      )

    s.valid_sel   = Wire ( 2 )

    s.connect( s.valid_sel[0],    s.validate_do   )
    s.connect( s.valid_sel[1],    s.invalidate_do )

    s.dirty_sel      = Wire ( 2 )

    s.connect( s.dirty_sel[0],    s.clean_do      )
    s.connect( s.dirty_sel[1],    s.dirty_do      )

  #-----------------------------------------------------------------------
  # Utility Functions
  #-----------------------------------------------------------------------

  def t( s, en, wen, ptr ):

    tag_cs = Bits( s.addr_nbits + 2 )

    tag_cs[ 0                   : s.addr_nbits     ] = ptr
    tag_cs[ s.addr_nbits     : s.addr_nbits + 1 ] = wen
    tag_cs[ s.addr_nbits + 1 : s.addr_nbits + 2 ] = en

    return tag_cs

  def v( s, wen, data, ptr ):

    valid_cs = Bits( s.addr_nbits + 2 )

    valid_cs[ 0                   : s.addr_nbits     ] = ptr
    valid_cs[ s.addr_nbits     : s.addr_nbits + 1 ] = data
    valid_cs[ s.addr_nbits + 1 : s.addr_nbits + 2 ] = wen

    return valid_cs

  def d( s, wen, data, ptr ):

    dirty_cs = Bits( s.addr_nbits + 2 )

    dirty_cs[ 0                   : s.addr_nbits     ] = ptr
    dirty_cs[ s.addr_nbits     : s.addr_nbits + 1 ] = data
    dirty_cs[ s.addr_nbits + 1 : s.addr_nbits + 2 ] = wen

    return dirty_cs

    #-----------------------------------------------------------------------
    # Combinational Logic
    #-----------------------------------------------------------------------

    @s.combinational
    def comb():

      # Local Constants

      n              = 0
      y              = 1

      # Method Encodings

      m_none         = 0b00

      m_search       = 0b01
      m_write        = 0b10

      m_validate     = 0b01
      m_invalidate   = 0b10

      m_clean        = 0b01
      m_dirty        = 0b10

      # output table for tag methods

      t_sel = s.tag_sel.value # Helper Signal
      t     = s.t             # Helper Function

      #                              tag tag tag
      #                              en  wen ptr
      if   t_sel == m_none  :t_cs=t( n,  n,  0                     )
      elif t_sel == m_search:t_cs=t( y,  n,  s.search_ptr.value )
      elif t_sel == m_write :t_cs=t( y,  y,  s.write_ptr.value  )
      else:
        assert False

      # output table for valid bit methods

      v_sel = s.valid_sel.value # Helper Signal
      v     = s.v               # Helper Function

      #                                  val val  val
      #                                  wen next ptr
      if   v_sel == m_none      :v_cs=v( n,  n,   0                         )
      elif v_sel == m_validate  :v_cs=v( y,  y,   s.validate_ptr.value   )
      elif v_sel == m_invalidate:v_cs=v( y,  n,   s.invalidate_ptr.value )
      else:
        assert False

      # output table for dirty bit methods

      d_sel = s.dirty_sel.value # Helper Signal
      d     = s.d               # Helper Function

      #                             dirty dirty dirty
      #                             wen   next  ptr
      if   d_sel == m_none :d_cs=d( n,    n,    0                    )
      elif d_sel == m_clean:d_cs=d( y,    n,    s.clean_ptr.value )
      elif d_sel == m_dirty:d_cs=d( y,    y,    s.dirty_ptr.value )
      else:
        assert False

      # Outputs

      s.ctrl_tag_ptr.value = t_cs[ 0                   : s.addr_nbits     ]
      s.ctrl_tag_wen.value = t_cs[ s.addr_nbits     : s.addr_nbits + 1 ]
      s.ctrl_tag_en.value  = t_cs[ s.addr_nbits + 1 : s.addr_nbits + 2 ]

      # give precedence to search method

      if s.search_do.value:
        s.ctrl_valid_ptr.value = t_cs[ 0 : s.addr_nbits ]
      else:
        s.ctrl_valid_ptr.value = v_cs[ 0 : s.addr_nbits ]
      s.ctrl_valid_next.value  = v_cs[ s.addr_nbits     : s.addr_nbits + 1 ]
      s.ctrl_valid_wen.value   = v_cs[ s.addr_nbits + 1 : s.addr_nbits + 2 ]

      # give precedence to search method

      if s.search_do.value:
        s.ctrl_dirty_ptr.value = t_cs[ 0 : s.addr_nbits ]
      else:
        s.ctrl_dirty_ptr.value = d_cs[ 0 : s.addr_nbits ]
      s.ctrl_dirty_next.value  = d_cs[ s.addr_nbits     : s.addr_nbits + 1 ]
      s.ctrl_dirty_wen.value   = d_cs[ s.addr_nbits + 1 : s.addr_nbits + 2 ]

#-------------------------------------------------------------------------
# DirectMappedWriteBackCacheTagArrayDpath
#-------------------------------------------------------------------------

# SearchMatch Model

class SearchMatch (Model):

  def __init__( s, tag_nbits ):

    s.valid      = InPort  ( 1 )
    s.tag_in     = InPort  ( tag_nbits )
    s.tag_rdata  = InPort  ( tag_nbits )

    s.match      = OutPort ( 1 )

  def elaborate_logic( s ):
    @s.combinational
    def comb():

      s.match.value = \
        s.valid.value & ( s.tag_in.value == s.tag_rdata.value )

# DirectMappedWriteBackCacheTagArrayDpath Model

class DirectMappedWriteBackCacheTagArrayDpath (Model):

  def __init__( s, num_entries, tag_nbits ):

    # address bits

    s.num_entries = num_entries
    s.tag_nbits = tag_nbits
    s.addr_nbits  = int( math.ceil( math.log( num_entries, 2 ) ) )

    # number of bytes

    s.num_bytes = ( tag_nbits + 7 ) / 8

    #---------------------------------------------------------------------
    # Interface Ports
    #---------------------------------------------------------------------

    # Search Method : search tag

    s.search_tag         = InPort  ( tag_nbits )

    # Write Method  : write tag

    s.write_tag          = InPort  ( tag_nbits )

    # Outputs

    s.search_match       = OutPort ( 1 )
    s.search_match_dirty = OutPort ( 1 )
    s.search_match_tag   = OutPort ( tag_nbits )

    # Control Signals (ctrl -> dpath)

    s.ctrl_tag_en        = InPort  ( 1 )
    s.ctrl_tag_wen       = InPort  ( 1 )
    s.ctrl_tag_ptr       = InPort  ( s.addr_nbits )

    s.ctrl_valid_wen     = InPort  ( 1 )
    s.ctrl_valid_next    = InPort  ( 1 )
    s.ctrl_valid_ptr     = InPort  ( s.addr_nbits )

    s.ctrl_dirty_wen     = InPort  ( 1 )
    s.ctrl_dirty_next    = InPort  ( 1 )
    s.ctrl_dirty_ptr     = InPort  ( s.addr_nbits )

  def elaborate_logic( s ):

    #---------------------------------------------------------------------
    # Datapath
    #---------------------------------------------------------------------

    # valid bits

    s.valid_bits = RAM_rst_1r1w( s.num_entries,
                                    1,
                                    reset_value = 0 )

    s.connect( s.valid_bits.wen,   s.ctrl_valid_wen  )
    s.connect( s.valid_bits.wdata, s.ctrl_valid_next )
    s.connect( s.valid_bits.waddr, s.ctrl_valid_ptr  )
    s.connect( s.valid_bits.raddr, s.ctrl_valid_ptr  )

    # dirty bits

    s.dirty_bits = RAM_rst_1r1w( s.num_entries,
                                    1,
                                    reset_value = 0 )

    s.connect( s.dirty_bits.wen,   s.ctrl_dirty_wen  )
    s.connect( s.dirty_bits.wdata, s.ctrl_dirty_next )
    s.connect( s.dirty_bits.waddr, s.ctrl_dirty_ptr  )
    s.connect( s.dirty_bits.raddr, s.ctrl_dirty_ptr  )

    # tag array

    CONST_ALL_ONES = ( 1 << num_bytes ) - 1

    s.tag_mem = SRAM1r1w( s.num_entries,
                             tag_nbits )

    s.connect( s.tag_mem.en,         s.ctrl_tag_en  )
    s.connect( s.tag_mem.wen,        s.ctrl_tag_wen )
    s.connect( s.tag_mem.byte_en,    CONST_ALL_ONES    )
    s.connect( s.tag_mem.addr,       s.ctrl_tag_ptr )
    s.connect( s.tag_mem.write_data, s.write_tag    )

    # valid rdata register

    s.valid_rdata_reg = pclib.regs.RegRst( 1, reset_value = 0 )

    s.connect( s.valid_rdata_reg.in_, s.valid_bits.rdata )

    # dirty rdata register

    s.dirty_rdata_reg = pclib.regs.RegRst( 1, reset_value = 0 )

    s.connect( s.dirty_rdata_reg.in_, s.dirty_bits.rdata )

    # search tag register

    s.search_tag_reg = pclib.regs.Reg( tag_nbits )

    s.connect( s.search_tag_reg.in_, s.search_tag )

    # search match logic

    s.smatch = SearchMatch( tag_nbits )

    s.connect( s.smatch.valid,     s.valid_rdata_reg.out )
    s.connect( s.smatch.tag_in,    s.search_tag_reg.out  )
    s.connect( s.smatch.tag_rdata, s.tag_mem.read_data   )

    # outputs

    s.connect( s.smatch.match,       s.search_match        )
    s.connect( s.search_match_dirty, s.dirty_rdata_reg.out )
    s.connect( s.search_match_tag,   s.tag_mem.read_data   )

#-------------------------------------------------------------------------
# DirectMappedWriteBackCacheTagArray
#-------------------------------------------------------------------------

class DirectMappedWriteBackCacheTagArray (Model):

  def __init__ ( s, num_entries = 16, tag_nbits = 26 ):

    # address bits

    s.num_entries = num_entries
    s.tag_nbits = tag_nbits
    s.addr_nbits = int( math.ceil( math.log( num_entries, 2 ) ) )

    #---------------------------------------------------------------------
    # Interface Ports
    #---------------------------------------------------------------------

    s.search_do          = InPort  ( 1 )
    s.search_ptr         = InPort  ( s.addr_nbits )
    s.search_tag         = InPort  ( s.tag_nbits  )
    s.search_match       = OutPort ( 1 )
    s.search_match_dirty = OutPort ( 1 )
    s.search_match_tag   = OutPort ( s.tag_nbits  )

    s.write_do           = InPort  ( 1 )
    s.write_ptr          = InPort  ( s.addr_nbits )
    s.write_tag          = InPort  ( s.tag_nbits  )

    s.validate_do        = InPort  ( 1 )
    s.validate_ptr       = InPort  ( s.addr_nbits )

    s.invalidate_do      = InPort  ( 1 )
    s.invalidate_ptr     = InPort  ( s.addr_nbits )

    s.clean_do           = InPort  ( 1 )
    s.clean_ptr          = InPort  ( s.addr_nbits )

    s.dirty_do           = InPort  ( 1 )
    s.dirty_ptr          = InPort  ( s.addr_nbits )

  #---------------------------------------------------------------------
  # Static elaboration
  #---------------------------------------------------------------------

  def elaborate_logic( s ):

    s.ctrl  = DirectMappedWriteBackCacheTagArrayCtrl( s.num_entries )
    s.dpath = DirectMappedWriteBackCacheTagArrayDpath( s.num_entries, s.tag_nbits )

    # Connect ctrl

    s.connect( s.ctrl.search_do,      s.search_do      )
    s.connect( s.ctrl.search_ptr,     s.search_ptr     )
    s.connect( s.ctrl.write_do,       s.write_do       )
    s.connect( s.ctrl.write_ptr,      s.write_ptr      )
    s.connect( s.ctrl.validate_do,    s.validate_do    )
    s.connect( s.ctrl.validate_ptr,   s.validate_ptr   )
    s.connect( s.ctrl.invalidate_do,  s.invalidate_do  )
    s.connect( s.ctrl.invalidate_ptr, s.invalidate_ptr )
    s.connect( s.ctrl.clean_do,       s.clean_do       )
    s.connect( s.ctrl.clean_ptr,      s.clean_ptr      )
    s.connect( s.ctrl.dirty_do,       s.dirty_do       )
    s.connect( s.ctrl.dirty_ptr,      s.dirty_ptr      )

    # Connect dpath

    s.connect( s.dpath.search_tag,         s.search_tag         )
    s.connect( s.dpath.search_match,       s.search_match       )
    s.connect( s.dpath.search_match_dirty, s.search_match_dirty )
    s.connect( s.dpath.search_match_tag,   s.search_match_tag   )
    s.connect( s.dpath.write_tag,          s.write_tag          )

    # Connect control signals (ctrl -> dpath)

    s.connect( s.ctrl.ctrl_tag_en,      s.dpath.ctrl_tag_en     )
    s.connect( s.ctrl.ctrl_tag_wen,     s.dpath.ctrl_tag_wen    )
    s.connect( s.ctrl.ctrl_tag_ptr,     s.dpath.ctrl_tag_ptr    )
    s.connect( s.ctrl.ctrl_valid_wen,   s.dpath.ctrl_valid_wen  )
    s.connect( s.ctrl.ctrl_valid_next,  s.dpath.ctrl_valid_next )
    s.connect( s.ctrl.ctrl_valid_ptr,   s.dpath.ctrl_valid_ptr  )
    s.connect( s.ctrl.ctrl_dirty_wen,   s.dpath.ctrl_dirty_wen  )
    s.connect( s.ctrl.ctrl_dirty_next,  s.dpath.ctrl_dirty_next )
    s.connect( s.ctrl.ctrl_dirty_ptr,   s.dpath.ctrl_dirty_ptr  )
