#-----------------------------------------------------------------------
# exceptions.py
#-----------------------------------------------------------------------

class VerilogTranslationError( Exception ):
  pass

class VerilatorCompileError( Exception ):
  pass

class IVerilogCompileError( Exception ):
  pass
