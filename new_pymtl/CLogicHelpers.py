from cffi import FFI

# Create position independent code
#cc_src = "g++ -O3 -fPIC -c -o {in}.cc {in}.h {out.o}"
#cc_lib = "g++ -shared -o libCSim.o {out}.so"

#-------------------------------------------------------------------------
# gen_cppsim
#-------------------------------------------------------------------------
def gen_cppsim( clib, cdef ):
  ffi = FFI()
  ffi.cdef( cdef )
  cmodule = ffi.dlopen( clib )
  return cmodule, ffi
  #return wrap( cmodule )

#-------------------------------------------------------------------------
# translate
#-------------------------------------------------------------------------
# Create the string passed into ffi.cdef
def gen_cdef( cycle_params ):
  str_    = '\n'
  str_   += 'void cycle({});\n'.format('\n'+cycle_params+'\n')
  str_   += 'unsigned int  ncycles;\n'
  #for name, cname, type_ in top_ports:
  #  str_ += '{} {}; // {}\n'.format( type_, cname, name )
  return str_

#-------------------------------------------------------------------------
# gen_cheader
#-------------------------------------------------------------------------
# Create the header for the simulator
def gen_cheader( cycle_params ):
  str_    = '\n'
  #str_   += '#ifndef CSIM_H\n'
  #str_   += '#define CSIM_H\n'
  str_   += 'extern "C" {\n'
  str_   += '  extern void cycle({});\n'.format('\n'+cycle_params+'\n')
  str_   += '  extern unsigned int ncycles;\n'
  #for name, cname, type_ in top_ports:
  #  str_ += '  extern {} {}; // {}\n'.format( type_, cname, name )
  str_   += '}\n'
  #str_   += '#endif\n'
  return str_

#-------------------------------------------------------------------------
# cycle_templ
#-------------------------------------------------------------------------
# Template for the cycle method in CSimWrapper
cycle_templ = """
def cycle( self, clk=0, reset=0 ):
  # Cycle Call
  self._cmodule.cycle(
    clk,
    reset,
    {}
  )
  # Store outputs
  {}
"""
#-------------------------------------------------------------------------
# gen_pywrapper
#-------------------------------------------------------------------------
# Create the header for the simulator
def gen_pywrapper( top_inports, top_outports ):

  #-----------------------------------------------------------------------
  # CSimWrapper
  #-----------------------------------------------------------------------
  # Inner class for generated python wrapper.
  # TODO: better way?
  class CSimWrapper( object ):

    def __init__( self, cmodule, ffi ):
      #self._model    = model
      self._cmodule  = cmodule
      self._ffi      = ffi

      # Create ffi types
      for fullname, net, type_ in top_outports:
        name = fullname[4:]  # remove 'top_' from name
        if '$' in name:
          sig, idx = name.split('$')
          setattr( self, '_'+sig,
                  [self._ffi.new( type_+'*' ) for x in range(int(idx)+1)] )
        else:
          setattr( self, '_'+name, self._ffi.new( type_+'*' ) )

    def reset( self ):
      self.cycle( reset=1 )
      self.cycle( reset=1 )

    @property
    def ncycles( self ):
      return self.cmodule.ncycles


  # Add input port attributes to CSimWrapper
  cparams  = []
  assigns  = []
  for fullname, _, _  in top_inports[2:]:
    name = fullname[4:]  # remove 'top_' from name
    # Handle lists specially
    # TODO: super hacky, only works if top_inports sorted by name
    if '$' in name:
      sig, idx = name.split('$')
      cparams.append( 'self.{}[{}]'.format(sig,idx) )
      setattr( CSimWrapper, sig, [0]*(int(idx)+1) )
    else:
      cparams.append( 'self.{}'.format(name) )
      setattr( CSimWrapper, name , 0 )

  # Add output port attributes to CSimWrapper
  for fullname, net, type_ in top_outports:
    name = fullname[4:]  # remove 'top_' from name
    # Handle lists specially
    # TODO: super hacky, only works if top_outports sorted by name
    if '$' in name:
      sig, idx = name.split('$')
      cparams.append( 'self._{}[{}]'.format(sig,idx) )
      assigns.append( 'self.{0}[{1}] = self._{0}[{1}][0]'.format(sig,idx) )
      setattr( CSimWrapper, sig, [0]*(int(idx)+1) )
      setattr( CSimWrapper, '_'+sig, [0]*(int(idx)+1) )
    else:
      cparams.append( 'self._'+name )
      assigns.append( 'self.{0} = self._{0}[0]'.format(name) )
      setattr( CSimWrapper, name , 0 )
      setattr( CSimWrapper, '_'+name , 0 )

  # TODO: SUPER HACKY PYTHON CODEGEN
  code = cycle_templ.format( ',\n    '.join( cparams ),
                             '\n  '   .join( assigns ) )

  # Create cycle method code and add it to the CSimWrapper
  exec( code ) in locals()
  CSimWrapper.cycle = cycle

  return CSimWrapper


#-------------------------------------------------------------------------
# gen_csim
#-------------------------------------------------------------------------
# TODO: not implemented, only works if generated code is pure C
def gen_csim( cstring, cdef ):
  raise Exception("Doesn't currently work!")
  ffi = FFI()
  ffi.cdef( cdef )
  clib = ffi.verify( cstring )
  return clib

