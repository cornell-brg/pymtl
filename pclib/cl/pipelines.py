#=======================================================================
# pipelines.py
#=======================================================================
# Collection of pipelines for cycle-level modeling.

from pymtl       import *
from collections import deque

#-----------------------------------------------------------------------
# Pipeline
#-----------------------------------------------------------------------
class Pipeline( object ):

  def __init__( self, stages=1 ):
    assert stages > 0
    self.stages = stages
    self.data   = deque( [None]*stages, maxlen = stages )

  def insert( self, item ):
    self.data[0] = item

  def remove( self ):
    item = self.data[-1]
    self.data[-1] = None
    return item

  def ready( self ):
    return self.data[-1] != None

  def advance( self ):
    self.data.rotate()

