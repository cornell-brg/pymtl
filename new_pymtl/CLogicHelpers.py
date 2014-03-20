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
def gen_cdef( cycle_params, top_ports ):
  str_    = '\n'
  str_   += 'void cycle({});\n'.format('\n'+cycle_params+'\n')
  str_   += 'unsigned int  ncycles;\n'
  for name, net, type_ in top_ports:
    str_ += '{} * _{};  // {}\n'.format( type_, name[4:], net )
  return str_

#-------------------------------------------------------------------------
# gen_cheader
#-------------------------------------------------------------------------
# Create the header for the simulator
def gen_cheader( cycle_params, top_ports ):
  str_    = '\n'
  str_   += 'extern "C" {\n'
  str_   += '  extern void cycle({}  );\n'.format('\n'+cycle_params+'\n')
  str_   += '  extern unsigned int ncycles;\n'
  for name, net, type_ in top_ports:
    str_ += '  extern {} * _{}; // {}\n'.format( type_, name[4:], net )
  str_   += '}\n'
  return str_

#-------------------------------------------------------------------------
# cycle_templ
#-------------------------------------------------------------------------
# Template for the cycle method in CSimWrapper
cycle_templ = """
def cycle( self, clk=0, reset=0 ):

  # Load Inputs
  {}

  # Cycle Call
  self._cmodule.cycle( clk, reset )

  # Store Outputs
  {}
"""
#-------------------------------------------------------------------------
# gen_pywrapper
#-------------------------------------------------------------------------
# Create the header for the simulator
def gen_pywrapper( top_inports, top_outports ):

  def name_splitter( name ):
    sig, idx = name.split('_IDX')
    sig = [sig] + idx.split('_')
    nonidx, idx = [], []
    for s in sig:
      (idx if s.isdigit() else nonidx).append(s)
    sig = '_'.join(nonidx)
    idx = idx[0]
    return sig, idx

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

    def reset( self ):
      self.cycle( reset=1 )
      self.cycle( reset=1 )

    @property
    def ncycles( self ):
      return self._cmodule.ncycles


  # Add input port attributes to CSimWrapper
  ld_inports  = []
  st_outports = []
  for fullname, net, type_  in top_inports[2:]:
    name = fullname[4:]  # remove 'top_' from name
    # Handle lists specially
    # TODO: super hacky, only works if top_inports sorted by name
    if '_IDX' in name:
      sig, idx = name_splitter(name)
      idx = int(idx)
      ld_inports.append( 'self._cmodule._{2}[0] = self.{0}[{1}]'
                         .format( sig, idx, name) )
      # Create "InPort" dummy attribute
      setattr( CSimWrapper,     sig, [0]*(idx+1) )
    else:
      ld_inports.append( 'self._cmodule._{0}[0] = self.{0}'.format(name) )
      # Create "InPort" dummy attribute
      setattr( CSimWrapper,     name , 0 )

  # Add output port attributes to CSimWrapper
  for fullname, net, type_ in top_outports:
    name = fullname[4:]  # remove 'top_' from name
    # Handle lists specially
    # TODO: super hacky, only works if top_outports sorted by name
    if '_IDX' in name:
      sig, idx = name_splitter(name)
      idx = int(idx)
      st_outports.append( 'self.{0}[{1}] = self._cmodule._{2}[0]'
                          .format( sig, idx, name ) )
      # Create "OutPort" dummy attribute
      setattr( CSimWrapper,     sig, [0]*(idx+1) )
    else:
      st_outports.append( 'self.{0} = self._cmodule._{0}[0]'.format(name) )
      # Create "OutPort" dummy attribute
      # Create signal attribute
      setattr( CSimWrapper,     name , 0 )

  # TODO: SUPER HACKY PYTHON CODEGEN
  code = cycle_templ.format( '\n  '.join( ld_inports  ),
                             '\n  '.join( st_outports ) )

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

