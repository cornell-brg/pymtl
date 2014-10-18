#=========================================================================
# MatrixVecBundle
#=========================================================================
# Hack! Need to_cpu port to be port bundle to make my proxy stuff work.

from new_pymtl import *

class MatrixVecBundle( PortBundle ):
  def __init__( self ):
    self.done = InPort(1)

InMatrixVecBundle, OutMatrixVecBundle = \
  create_PortBundles( MatrixVecBundle )

