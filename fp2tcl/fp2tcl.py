#!/usr/bin/env python
import sys
import argparse
import fileinput
import os
import re

if __name__ == '__main__':

  parser = argparse.ArgumentParser()
  parser.add_argument('filename', metavar='floorplan_spec', help='floorplan specification')

  args = parser.parse_args()

  filename = args.filename

  f = open( filename, 'r' )

  s = f.readline()
  s = s.strip()

  while s[0] == '#':
    s = f.readline()
    s = s.strip()
  
  s = re.sub( ' ', '', s )
  s = re.sub( 'top\(', '', s )
  s = re.sub( '\)', '', s )
  s = re.sub( ',', ' ', s )
  l = s.split()
  core_width = int( l[-2] )
  core_height = int( l[-1] )

  modules = []

  io_spacing = 30

  s = f.readline()

  while 'top' in s:
    s = re.sub(' ', '', s )
    s = re.sub('top.', '', s )
    s = re.sub('\(', ' ', s )
    s = re.sub(',', ' ', s )
    s = re.sub('\)', ' ', s )
    l = s.split()

    m = l[0]
    x1 = int(l[1])
    y1 = int(l[2])
    x2 = x1 + int(l[3])
    y2 = y1 + int(l[4])
    modules.append( ( m, ( x1 + io_spacing, y1 + io_spacing, x2 + io_spacing, y2 + io_spacing ) ) )
    s = f.readline()

  f.close()

  f = open( 'fp.tcl', 'w' )

  w = '\
initialize_floorplan \\\n\
        -control_type width_and_height \\\n\
        -core_width {0} \\\n\
        -core_height {1} \\\n\
        -row_core_ratio 1 \\\n\
        -left_io2core 30 \\\n\
        -bottom_io2core 30 \\\n\
        -right_io2core 30 \\\n\
        -top_io2core 30 \\\n\
        -start_first_row\n\n'.format( core_width, core_height )

  for m in modules:
    coords = m[1]
    w += 'create_plan_groups \\\n\
        -coordinate {5}{0} {1} {2} {3}{6} \\\n\
        -is_fixed \\\n\
        -cycle_color \\\n\
        {4}\n\n'.format( coords[0], coords[1], coords[2], coords[3], m[0], '{', '}' )

  f.write(w)

  f.close()
