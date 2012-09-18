#=========================================================================
# Sparse Memory Image
#=========================================================================
# This module contains a class for representing ELF sections to load a
# TestMemory object.

import subprocess
import tempfile

from pymtl import *

#-------------------------------------------------------------------------------
# Global Variables
#-------------------------------------------------------------------------------

objdump_cmd  = "maven-objdump -DC --disassemble-zeroes --section=.text "
objdump_cmd += "--section=.data --section=.sdata --section=.xcpthandler "
objdump_cmd += "--section=.init --section=.fini --section=.ctors "
objdump_cmd += "--section=.dtors --section=.eh_frame --section=.jcr "
objdump_cmd += "--section=.sbss --section=.bss --section=.rodata "
objdump_cmd += "%(filename)s > %(tempfilename)s"

#-------------------------------------------------------------------------------
# Utility Functions
#-------------------------------------------------------------------------------

def execute( cmd ):
  print cmd
  try:
    subprocess.call( cmd, shell=True )
  except  subprocess.CalledProcessError, err:
    print "ERROR: " + err.output

#-------------------------------------------------------------------------------
# Sparse Memory Image Class
#-------------------------------------------------------------------------------

class SparseMemoryImage:

  #-----------------------------------------------------------------------------
  # Constructor
  #-----------------------------------------------------------------------------

  def __init__( self, string = None, filename = None ):

    # sparse memory : list of list of lists
    # a single entry in the class represents a section header along with
    # the bytes of memory stored in the section.
    # [ section_addr, [list of bytes] ]
    self.sparse_memory_img = [ ]

    if string is not None:

      # Actions when an assembly string is passed
      pass

    elif filename is not None:

      # Create a temporary file for capturing objdump output and pass the
      # filename to objdump command and execute the objdump command

      temp = tempfile.NamedTemporaryFile( mode = 'rw' )
      cmd = objdump_cmd % { "filename" : filename, "tempfilename" : temp.name }
      execute( cmd )

      # move to the start of the temp file
      temp.seek( 0 )

      # fill the sparse memory sections

      in_section = False
      for line in temp:

        split_line = line.split()

        # start of a section

        if( line.find( ">:\n" ) >= 0 ):

          bytes_list   = []
          in_section   = True
          section_addr = int( split_line[0], 16 )

          # block_name = split_line[1][:-1]

        elif in_section:


          if line == "\n":

            # end of a section

            in_section = False
            self.sparse_memory_img.append( [ section_addr, bytes_list ] )

          else:

            # append bytes insided a section

            inst_bits      = Bits( 32 )
            inst_bits.uint = int( split_line[1], 16 )

            for i in xrange( 4 ):
              bytes_list.append( inst_bits[i*8:i*8+8].uint )

      # close temporary file

      temp.close()

  #-----------------------------------------------------------------------------
  # load section method
  #-----------------------------------------------------------------------------

  def load_section( self, section_list ):
    self.sparse_memory_img.append( section_list )

  #-----------------------------------------------------------------------------
  # read section method
  #-----------------------------------------------------------------------------

  def read_section( self, section_addr ):
    return self.sparse_memory_img[ section_addr ]

  #-----------------------------------------------------------------------------
  # num sections method
  #-----------------------------------------------------------------------------

  def num_sections( self ):
    return len( self.sparse_memory_img )
