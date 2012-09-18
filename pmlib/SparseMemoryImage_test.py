#=========================================================================
# Sparse Memory Image Test Suite
#=========================================================================

from SparseMemoryImage import SparseMemoryImage

#-------------------------------------------------------------------------------
# test_smi_str_labels_list
#-------------------------------------------------------------------------------
# This test compares the sparse memory image created by passing an assembly
# string to a manually assembled image.

def test_smi_str_labels_list( dump_asm, dump_bin ):

  asm_file = None
  bin_file = None

  if dump_asm:
    asm_file = "simple-addiu.s"

  if dump_bin:
    bin_file = "simple-addiu"

  # obtained by manual conversion

  labels_list = [ [8421376, [1, 0, 67, 36]],
                  [8421380, [1, 0, 2, 36, 0, 0, 29, 36, 0, 8, 157, 64, 255,
                   255, 2, 20, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]],
                  [8421556, [1, 0, 2, 36, 0, 128, 3, 60, 37, 232, 163, 3, 0,
                   8, 157, 64, 255, 255, 2, 20, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0]] ]

  mem_img_from_labels_list = SparseMemoryImage( labels_list = labels_list )

  mem_img_from_str = SparseMemoryImage( asm_str  = "addiu $3, $2, 1",
                                        dump_asm = asm_file,
                                        dump_bin = bin_file )

  assert mem_img_from_str == mem_img_from_labels_list

#-------------------------------------------------------------------------------
# test_smi_str_bin
#-------------------------------------------------------------------------------
# This is a throw away test which assumes the availability of a binary file
# which has been assembled using the cross compiler and compares the memory
# images created by passing an assembly string to that obtained by passing
# the actual binary file.
#
#def test_smi_str_bin():
#
#  mem_img_from_bin_file = SparseMemoryImage( bin_filename = 'simple-addiu' )
#  mem_img_from_str = SparseMemoryImage( asm_str = "addiu $3, $2, 1" )
#
#  assert mem_img_from_str == mem_img_from_bin_file
#
#-------------------------------------------------------------------------------
# test_smi_bin_labels_list
#-------------------------------------------------------------------------------
# This is a throw away test which assumes the availability of a binary file
# which has been assembled using the cross compiler and compares the memory
# images created by passing a labels_list to that obtained by passing
# the actual binary file.
#
#def test_smi_bin_labels_list():
#
#  # obtained by manual conversion
#
#  labels_list = [ [8421376, [1, 0, 67, 36]],
#                  [8421380, [1, 0, 2, 36, 0, 0, 29, 36, 0, 8, 157, 64, 255,
#                   255, 2, 20, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
#                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
#                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
#                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
#                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
#                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
#                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
#                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
#                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]],
#                  [8421556, [1, 0, 2, 36, 0, 128, 3, 60, 37, 232, 163, 3, 0,
#                   8, 157, 64, 255, 255, 2, 20, 0, 0, 0, 0, 0, 0, 0, 0, 0,
#                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
#                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
#                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
#                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
#                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
#                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
#                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
#                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
#                   0, 0, 0, 0, 0, 0, 0]] ]
#
#  mem_img_from_labels_list = SparseMemoryImage( labels_list = labels_list )
#
#  mem_img_from_bin_file = SparseMemoryImage( bin_filename = 'simple-addiu' )
#
#  assert mem_img_from_bin_file == mem_img_from_labels_list
