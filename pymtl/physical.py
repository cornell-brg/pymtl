#=========================================================================
# Physical Elaboration
#=========================================================================

#-------------------------------------------------------------------------
# PhysicalDimensions
#-------------------------------------------------------------------------

class PhysicalDimensions(object):

  def __init__( self ):
    self.x = 0
    self.y = 0
    self.h = 0
    self.w = 0

  def get_rectangle( self ):
    x, y, h, w = self.x, self.y, self.h, self.w
    return (x, y, h, w)

  def get_bounding_box( self ):
    # assumes origin is top left!
    x, y, h, w = self.x, self.y, self.h, self.w
    tl = ( x,     y     )  # top_left
    tr = ( x + w, y     )  # top_right
    bl = ( x,     y + h )  # bottom_left
    br = ( x + w, y + h )  # bottom_right
    return [ tl, tr, bl, br ]

