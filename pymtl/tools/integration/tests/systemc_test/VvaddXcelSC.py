#=========================================================================
# VvaddXcelSC
#=========================================================================
# Wrapper module for SystemC implementation.
# This file should be hand-written.

from pymtl       import *
from pclib.ifcs  import InValRdyBundle, OutValRdyBundle
from pclib.ifcs  import MemReqMsg, MemRespMsg
from RoccCoreMsg import RoccCoreCmdMsg, RoccCoreRespMsg

# SystemCModel instead of VerilogModel
# PyMTL assumes the module name is the same as the class name.

class VvaddXcelSC( SystemCModel ): 
  
  def __init__( s ):
    
    # Port definition, the same thing as we do for verilog import
    
    s.xcelreq  = InValRdyBundle  ( RoccCoreCmdMsg()  )
    s.xcelresp = OutValRdyBundle ( RoccCoreRespMsg() )

    s.memreq   = OutValRdyBundle( MemReqMsg (8,32,32) )
    s.memresp  = InValRdyBundle ( MemRespMsg(8,32)    )
    
    # Specify the source file here. PyMTL assumes that the order is the same
    # as gcc make order.
    # For exampple, if VvaddXcelSC.cc has some dependency on msgs.cc
    # then msgs should strictly follows VvaddXcelSC on this list.
    # 
    # PyMTL is able to automatically detect the extension of the source
    # files in {".cpp", ".cc", ".cxx", ".c++"}, as well as headers in
    # {".h", ".hh", ".hpp", ".h++" }.
    #
    # If no specified source file is found in all source folders,
    # PyMTL will raise error.
    
    s.sourcefile   = [
      "VvaddXcelSC",
      "msgs",
    ]
    
    # Specify the source folders here, PyMTL will try to look for
    # combinations of folder and source file.
    #
    # If your source file includes some file from other folder, then 
    # please add it here as well.
    #
    # There are two ways to specify the path
    # - If a path string starts with "/" then PyMTL will see it as 
    #   an absolute path.
    # - Otherwise PyMTL will concatenate the path of this file with
    #   the relative path.
    
    s.sourcefolder = [
      "sc_module",
      "util",
      # /home/.../util
    ]

    # Tell PyMTL the corresponding ports of your SystemC design 
    # < SystemC port name : PyMTL port name in the port definition >
    
    s.set_ports({
      'clk'          : s.clk,
      'rst'          : s.reset,
      
      'xcelreq_msg'  : s.xcelreq.msg,
      'xcelreq_val'  : s.xcelreq.val,
      'xcelreq_rdy'  : s.xcelreq.rdy,
      'xcelresp_msg' : s.xcelresp.msg,
      'xcelresp_val' : s.xcelresp.val,
      'xcelresp_rdy' : s.xcelresp.rdy,
      
      'memreq_msg'   : s.memreq.msg,
      'memreq_val'   : s.memreq.val,
      'memreq_rdy'   : s.memreq.rdy,
      'memresp_msg'  : s.memresp.msg,
      'memresp_val'  : s.memresp.val,
      'memresp_rdy'  : s.memresp.rdy
    })
    
