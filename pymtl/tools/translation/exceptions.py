#=======================================================================
# exceptions.py
#=======================================================================

#-----------------------------------------------------------------------
# VerilogTranslationError
#-----------------------------------------------------------------------
class VerilogTranslationError( Exception ):
  def __init__( self, message, lineno=None ):
    super( VerilogTranslationError, self ).__init__( message )
    self.lineno = lineno

#-----------------------------------------------------------------------
# VerilatorCompileError
#-----------------------------------------------------------------------
class VerilatorCompileError( Exception ):
  pass

#-----------------------------------------------------------------------
# IVerilogCompileError
#-----------------------------------------------------------------------
class IVerilogCompileError( Exception ):
  pass
