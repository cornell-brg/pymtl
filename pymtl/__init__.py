#-----------------------------------------------------------------------
# model components
#-----------------------------------------------------------------------

from model.Model      import Model
from model.signals    import Wire, InPort, OutPort
from model.PortBundle import PortBundle, create_PortBundles

#-----------------------------------------------------------------------
# data types
#-----------------------------------------------------------------------

from datatypes.Bits        import Bits
from datatypes.BitStruct   import BitStruct, BitStructDefinition, BitField
from datatypes.helpers     import (
    get_nbits, get_sel_nbits, zext, sext, concat,
    reduce_and, reduce_or, reduce_xor
)
from datatypes.SignalValue import CreateWrappedClass

#-----------------------------------------------------------------------
# tools
#-----------------------------------------------------------------------

from tools.simulation.SimulationTool import SimulationTool
from tools.translation.verilator_sim import TranslationTool
from tools.translation.cpp_sim       import get_cpp

#-----------------------------------------------------------------------
# py.test decorators
#-----------------------------------------------------------------------

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

#-----------------------------------------------------------------------
# pymtl namespace
#-----------------------------------------------------------------------

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
            'TranslationTool',
            # TEMPORARY
            'get_cpp',
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

