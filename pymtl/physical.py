#=========================================================================
# Physical Elaboration
#=========================================================================

import sys
MARGIN = 20

#-------------------------------------------------------------------------
# PhysicalDimensions Container Class
#-------------------------------------------------------------------------

class PhysicalDimensions(object):

  def __init__( self ):
    self.x = 0
    self.y = 0
    self.w = 0
    self.h = 0

  def get_rectangle( self ):
    x, y, w, h = self.x, self.y, self.w, self.h
    return (x, y, w, h)

  def get_bounding_box( self ):
    # assumes origin is top left!
    x, y, w, h = self.x, self.y, self.w, self.h
    tl = ( x,     y     )  # top_left
    tr = ( x + w, y     )  # top_right
    bl = ( x,     y + h )  # bottom_left
    br = ( x + w, y + h )  # bottom_right
    return [ tl, tr, bl, br ]

#-------------------------------------------------------------------------
# PhysicalToDiagram
#-------------------------------------------------------------------------

class PhysicalDiagramTool():

  #-----------------------------------------------------------------------
  # Constructor
  #-----------------------------------------------------------------------

  def __init__(self, model, o=sys.stdout):

    if not model.is_elaborated():
      msg  = "cannot initialize {0} tool.\n".format(self.__class__.__name__)
      msg += "Provided model has not been elaborated yet!!!"
      raise Exception(msg)

    self.model = model

    # Take either a string or a output stream
    if isinstance(o, str):
      o = open(o, 'w')

    rectangles = self.get_physical_design( self.model )

    #import pprint
    #pprint.pprint( rectangles )
    self.generate_svg( rectangles, o )

  #-----------------------------------------------------------------------
  # Generate SVG File
  #-----------------------------------------------------------------------

  def generate_svg( self, rectangles, o ):
    x,y,w,h = rectangles[0][1]
    w += MARGIN*2
    h += MARGIN*2
    print >> o, "<svg width='{}' height='{}'>".format( w, h )
    for name, dim in rectangles:
      print >> o, "  " + self.dim_to_svg_rect( name, dim )
    print >> o, "</svg>"

  #-----------------------------------------------------------------------
  # Create SVG Rectangle Object
  #-----------------------------------------------------------------------

  def dim_to_svg_rect( self, name, rect ):
    x, y, w, h = rect
    x += MARGIN
    y += MARGIN
    dims  = "x='{}' y='{}' width='{}' height='{}'".format(x,y,w,h)
    color = 'white' if name == 'top' else 'gray'
    dash  = 'stroke-dasharray: 2, 2;' if name == 'top' else ''
    style = "style='fill: {}; stroke:black; stroke-width:1; {}'".format(
        color, dash )
    name  = "<!-- {} -->".format( name )
    return "<rect {} {} />".format( dims, style )

  #-----------------------------------------------------------------------
  # Get Rectangles from Physical Design
  #-----------------------------------------------------------------------

  def get_physical_design( self, model, prefix='' ):
    if prefix:
      fullname = prefix + '.' + model.name
    else:
      fullname = model.name

    dimensions = model._dim.get_rectangle()
    rectangles = [ (fullname, dimensions) ]

    for submod in model.get_submodules():
      rectangles.extend( self.get_physical_design( submod, fullname ) )

    return rectangles

#=========================================================================
# Main
#=========================================================================

def main():

  # Get the model we want to translate from the commandline
  model_name = sys.argv[1]

  # Use some trickery to import the module containing the model
  __import__( model_name )
  imported_module = sys.modules[ model_name ]

  # Get the model class from the module, instantiate and elaborate it
  model_class = imported_module.__dict__[ model_name ]
  model_inst = model_class()
  model_inst.elaborate()
  model_inst.physical_elaboration()

  # Translate
  # TODO: add commandline option for output file name
  PhysicalDiagramTool( model_inst )

#-------------------------------------------------------------------------
# Main Check
#-------------------------------------------------------------------------

if __name__ == "__main__":
  main()
