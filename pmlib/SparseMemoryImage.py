#=========================================================================
# Sparse Memory Image
#=========================================================================
# This module contains a class for representing ELF sections to load a
# TestMemory object.

class SparseMemoryImage:

  def __init__( self ):

    # sparse memory : list of list of lists
    # a single entry in the class represents a section header along with
    # the bytes of memory stored in the section.
    # [ section_addr, [list of bytes] ]
    self.sparse_memory_img = [ ]

  def load_section( self, section_list ):
    self.sparse_memory_img.append( section_list )

  def read_section( self, section_addr ):
    return self.sparse_memory_img[ section_addr ]

  def num_sections( self ):
    return len( self.sparse_memory_img )
