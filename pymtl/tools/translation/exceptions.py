#-----------------------------------------------------------------------
# exceptions.py
#-----------------------------------------------------------------------

class VerilogTranslationError( Exception ):
  def __init__( self, message, lineno=None ):
    super( VerilogTranslationError, self ).__init__( message )
    self.lineno = lineno

class VerilatorCompileError( Exception ):
  pass

class IVerilogCompileError( Exception ):
  pass
