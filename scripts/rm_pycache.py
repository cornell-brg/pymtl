#! /usr/bin/env python
#========================================================================
# rm_pycache.py
#========================================================================
# Utility script to remove all .pyc files and __pycache__ directories.

from __future__ import print_function

import os

def main():

  for root, dirs, files in os.walk('.'):
    pycaches = [os.path.join(root, x) for x in dirs if x == '__pycache__']
    for i in pycaches:
      print( 'rm: {}'.format(i) )
      os.system( 'rm -r {}'.format(i) )

  for root, dirs, files in os.walk('.'):
    pycs = [os.path.join(root, x) for x in files if x.endswith('.pyc')]
    for i in pycs:
      print( 'rm: {}'.format(i) )
      os.remove( i )

if __name__ == "__main__":
  main()
