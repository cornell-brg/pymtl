#=========================================================================
# VerilogLogicTransl_test.py
#=========================================================================

from CLogicTransl import CLogicTransl
from subprocess   import check_output, STDOUT, CalledProcessError
from SignalValue  import CreateWrappedClass
from Model        import *

import tempfile

compiler = 'gcc -Wall'

#-------------------------------------------------------------------------
# translate
#-------------------------------------------------------------------------
def translate( model ):
  model.elaborate()

  with tempfile.NamedTemporaryFile(suffix='.cpp') as output:
    CLogicTransl( model, output )
    output.flush()
    cmd  = '{} {}'.format( compiler, output.name )

    try:

      result = check_output( cmd.split() , stderr=STDOUT )
      output.seek(0)
      source = output.read()
      print
      print source
      run    = check_output( './a.out' )
      print '...EXECUTING'+'.'*20
      print run
      print '............'+'.'*20

    except CalledProcessError as e:

      output.seek(0)
      source = output.read()

      raise Exception( 'Module did not compile!\n\n'
                       'Command:\n' + ' '.join(e.cmd) + '\n\n'
                       'Error:\n' + e.output + '\n'
                       'Source:\n' + source
                     )



#-------------------------------------------------------------------------
# NetObject
#-------------------------------------------------------------------------
class _NetObject( object ):
  def __init__( self, dest=0, src=0, seqnum=0, payload=0 ):
    self.dest    = dest
    self.src     = src
    self.seqnum  = seqnum
    self.payload = payload

NetObject = CreateWrappedClass( _NetObject )

#-------------------------------------------------------------------------
# Register
#-------------------------------------------------------------------------
class Register( Model ):
  def __init__( s ):
    s.in_ = InPort ( NetObject )
    s.out = OutPort( NetObject )
  def elaborate_logic( s ):
    @s.tick
    def logic():
      s.out.next = s.in_

#-------------------------------------------------------------------------
# test_Register
#-------------------------------------------------------------------------
def test_Register():
  translate( Register() )
