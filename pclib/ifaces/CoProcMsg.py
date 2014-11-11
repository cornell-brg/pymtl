from pymtl import *

class CoProcMsg( object ):
    def __init__( s, addr_nbits, data_nbits ):
        s.req  = CoProcReqMsg ( addr_nbits, data_nbits)
        s.resp = CoProcRespMsg( data_nbits            )

class CoProcReqMsg( BitStructDefinition ):

  def __init__( s, addr_nbits, data_nbits):

    s.addr_nbits = addr_nbits
    s.data_nbits = data_nbits

    s.addr = BitField( s.addr_nbits )
    s.data = BitField( s.data_nbits )

  def mk_msg( s, type_, addr, len_, data):

    msg      = s()

    return msg


#-------------------------------------------------------------------------
# MemReqMsg
#-------------------------------------------------------------------------
# BitStruct designed to create memory response messages.
class CoProcRespMsg ( BitStructDefinition ):

  def __init__( s, data_nbits):

    s.data_nbits = data_nbits

    s.data = BitField( s.data_nbits )

    #TODO mk_msg

  def unpck( s, msg):

    resp = s()
    resp.value = msg
    return resp
