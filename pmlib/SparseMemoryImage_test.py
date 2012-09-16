#=========================================================================
# Sparse Memory Image Test Suite
#=========================================================================

from SparseMemoryImage import SparseMemoryImage

def test_sparse_memory_img():

  sparse_mem_img = SparseMemoryImage()

  section_0 = [  0x000010000, [
                 0x00,
                 0x01,
                 0x02,
                 0x03,
                 0x04,
                 0x05,
                 0x06,
                 0x07 ]
              ]

  section_1 = [  0x000040000, [
                 0x00,
                 0x01,
                 0x02,
                 0x03,
                 0x04,
                 0x05,
                 0x06,
                 0x07 ]
              ]

  sparse_mem_img.load_section( section_0 )
  sparse_mem_img.load_section( section_1 )

  assert sparse_mem_img.num_sections()    == 2
  assert sparse_mem_img.read_section( 0 ) == section_0
  assert sparse_mem_img.read_section( 1 ) == section_1
