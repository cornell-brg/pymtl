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
# gen_pywrapper
#-------------------------------------------------------------------------
# Create the header for the simulator
def gen_pywrapper( top_inports, top_outports ):

  class CSimWrapper( object ):

    def __init__( self, cmodule, ffi ):
      #self._model    = model
      self._cmodule  = cmodule
      self._ffi      = ffi
      self._inports  = []
      self._outports = []

      # Skip clk and reset
      for fullname, _, _  in top_inports[2:]:
        name = fullname[4:]  # remove 'top_' from name
        setattr( self, name , 0 )
        self._inports.append( name )

      for fullname, net, type_ in top_outports:
        name = fullname[4:]  # remove 'top_' from name
        setattr( self, name, 0 )
        setattr( self, '_'+name, self._ffi.new( type_+'*' ) )
        self._outports.append( name )

    def cycle( self, clk=0, reset=0 ):
      # TODO: replace this with properties?
      in_args  = [ getattr( self, x )     for x in self._inports  ]
      out_args = [ getattr( self, '_'+x ) for x in self._outports ]
      self._cmodule.cycle( clk, reset, *(in_args + out_args) )
      for i in self._outports:
        setattr( self, i, getattr( self, '_'+i )[0] )

    def reset( self ):
      self.cycle( reset=1 )
      self.cycle( reset=1 )

    @property
    def ncycles( self ):
      return self.cmodule.ncycles

  #  # Port lists
  #  if '$' in name:
  #    sig, idx = name.split('$')
  #    if not hasattr( CSimWrapper, sig ):
  #      portlist = ListAccessor( CSimWrapper )
  #      setattr( CSimWrapper, sig, portlist )
  #    else:
  #      portlist = getattr( CSimWrapper, sig )
  #    portlist.lookup[ int(idx) ] = cname

  #  # Normal ports
  #  else:
  #    make_accessor( name, cname )

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

