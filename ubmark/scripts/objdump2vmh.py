#!/usr/bin/env python
#===============================================================================
# objdump2vmh.py
#===============================================================================
#
#  -h --help     Display this message
#  -v --verbose  Verbose mode
#  -f --file     Objdump file to parse
#
# Author : Ji Kim
# Date   : April 13, 2011
#

import optparse
import fileinput
import sys
import re

#-------------------------------------------------------------------------------
# Command line processing
#-------------------------------------------------------------------------------

class OptionParserWithCustomError(optparse.OptionParser):
  def error( self, msg = "" ):
    if ( msg ): print("\n ERROR: %s" % msg)
    print("")
    for line in fileinput.input(sys.argv[0]):
      if ( not re.match( "#", line ) ): sys.exit(msg != "")
      if ((fileinput.lineno() == 3) or (fileinput.lineno() > 4)):
        print( re.sub( "^#", "", line.rstrip("\n") ) )

def parse_cmdline():
  p = OptionParserWithCustomError( add_help_option=False )
  p.add_option( "-v", "--verbose", action="store_true", dest="verbose" )
  p.add_option( "-h", "--help",    action="store_true", dest="help" )
  p.add_option( "-f", "--file",    action="store", type="string", dest="file" )
  (opts,args) = p.parse_args()
  if ( help == True ): p.error()
  if args: p.error("found extra positional arguments")
  return opts

#-------------------------------------------------------------------------------
# Main
#-------------------------------------------------------------------------------

def main():
  opts = parse_cmdline()

  # Open vmh file for writing
  file_out = open( opts.file[0:opts.file.find( "." )] + ".vmh", "w" )

  try:

    file_out.write( "\n" )

    # Open objdump file for reading
    file_in = open( opts.file, "r" )

    try:

      in_block = False

      # Iterate through lines in the file
      for line in file_in:

        # Parse the line into a list of words
        split_line = line.split()

        # Check if line is the beginning of an instruction block
        if ( line.find( ">:" ) >= 0 ):

          in_block = True

          # Convert block virtual address to physical address
          block_addr = hex( int( split_line[0], 16 ) )[2:]

          # Name of current block
          block_name = split_line[1][:-1]

          # Number of spaces between address and comment, offset from left edge = 10
          space_amt = ( 10 - ( len( block_addr ) + 1 ) )

          # Construct vmh line to write
          buffer = "@" + block_addr + ( " " * space_amt ) + "// " + block_name + "\n"

          # Write to vmh file
          file_out.write( buffer )

        # Check if line is within an instruction block
        elif ( in_block ):

          # Unset in_block if there's a break
          if ( line == "\n" ):

            in_block = False
            file_out.write( "\n" )

          else:

            # Parse instruction fields
            inst_bits = split_line[1]
            PC_raw = split_line[0][:-1]
            zero_amt = 8 - len( PC_raw )
            PC = ( "0" * zero_amt ) + PC_raw

            # Iterate through bytes in current data word
            bytes = range(4)
            bytes.reverse()

            for i in bytes:

              # Construct vmh line to write
              buffer = inst_bits[i*2:i*2+2]

              if ( i == 3 ):
                buffer = buffer + "        // " + PC + "\n"
              else:
                buffer = buffer + "\n"

              # Write line to file
              file_out.write( buffer )

    finally:

      file_in.close()

  finally:

    file_out.close()

main()

