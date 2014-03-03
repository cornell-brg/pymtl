#------------------------------------------------------------------------------
# PyMTL components
#------------------------------------------------------------------------------

from Model          import Model
from signals        import Wire, InPort, OutPort
from Bits           import Bits
from SimulationTool import SimulationTool
from PortBundle     import PortBundle, create_PortBundles
from BitStruct      import BitStruct, BitStructDefinition, BitField
from helpers        import get_nbits, get_sel_nbits, zext, sext, concat
from helpers        import reduce_and, reduce_or, reduce_xor
from SignalValue    import CreateWrappedClass

#------------------------------------------------------------------------------
# py.test decorators
#------------------------------------------------------------------------------

from pytest          import mark
from distutils.spawn import find_executable
from os.path         import exists

has = lambda x: find_executable( x ) != None

requires_xcc = mark.skipif( not( has('maven-gcc') and has('maven-objdump') ),
                            reason='requires cross-compiler toolchain' )

requires_vmh = mark.skipif( not exists('../tests/build/vmh'),
                            reason='requires vmh files' )

requires_iverilog  = mark.skipif( not( has('iverilog') ),
                                  reason='requires iverilog' )

requires_verilator = mark.skipif( not( has('verilator') ),
                                  reason='requires verilator' )

#------------------------------------------------------------------------------
# new_pymtl namespace
#------------------------------------------------------------------------------

__all__ = [ # Model Construction
            'Model',
            # Signals
            'InPort',
            'OutPort',
            'Wire',
            'PortBundle',
            'create_PortBundles',
            # Message Types
            'Bits',
            'BitStruct',
            # Message Constructors
            'BitStructDefinition',
            'BitField',
            # Tools
            'SimulationTool',
            # TEMPORARY
            'CreateWrappedClass',
            # Helper Functions
            'get_nbits',
            'get_sel_nbits',
            'sext',
            'zext',
            'concat',
            'reduce_and',
            'reduce_or',
            'reduce_xor',
            # py.test decorators
            'requires_xcc',
            'requires_vmh',
            'requires_iverilog',
            'requires_verilator',
          ]

