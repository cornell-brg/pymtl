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

  str_   += 'typedef struct {\n'
  for name, net, type_ in top_ports:
    str_ += '  {} {};  // {}\n'.format( type_, name[4:], net )
  str_   += '} iface_t;\n\n'

  str_   += 'void cycle({});\n\n'.format('\n'+cycle_params+'\n')

  str_   += 'unsigned int  ncycles;\n'
  print str_
  return str_

#-------------------------------------------------------------------------
# gen_cheader
#-------------------------------------------------------------------------
# Create the header for the simulator
def gen_cheader( cycle_params, top_ports ):
  str_    = '\n'

  str_   += 'extern "C" {\n'

  str_   += '  typedef struct {\n'
  for name, net, type_ in top_ports:
    str_ += '    {} {};  // {}\n'.format( type_, name[4:], net )
  str_   += '  } iface_t;\n\n'

  str_   += '  extern void cycle({}  );\n'.format('\n'+cycle_params+'\n')
  str_   += '  extern unsigned int ncycles;\n'

  str_   += '};\n'
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
  self._cmodule.cycle( clk, reset, self._top )

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
      self._top      = ffi.new("iface_t *")

      #-------------------------------------------------------------------
      # CSimWrapper
      #-------------------------------------------------------------------
      # Utilty ListWrapper class for lists of ports
      class ListWrapper( object ):
        def __init__( self, top ):
          #self._top = top
          self._get = {}
          self._set = {}

        def __getitem__( self, key ):
          return self._get[ key ]( self )

        def __setitem__( self, key, value ):
          self._set[ key ]( self, value )

      #-------------------------------------------------------------------
      # create_fget
      #-------------------------------------------------------------------
      # Utilty method for creating fget
      def create_fget( top, name ):
        return lambda self: getattr( top[0], name )

      #-------------------------------------------------------------------
      # create_fset
      #-------------------------------------------------------------------
      # Utilty method for creating fset
      def create_fset( top, name ):
        return lambda self, value : setattr( top[0], name, value )

      # Add properties for all cffi exposed toplevel ports
      for fullname, net, type_ in top_inports[2:] + top_outports:

        name = fullname[4:]

        # This signal is a list of ports, use a ListWrapper object )
        if '_IDX' in name:
          sig, idx = name_splitter(name)

          if not hasattr( self, sig ):
            setattr( self, sig, ListWrapper( self._top ) )

          getattr( self, sig )._get[int(idx)] = create_fget( self._top, name )
          getattr( self, sig )._set[int(idx)] = create_fset( self._top, name )

        # This signal is a single port, create a property
        else:
          fget = create_fget( self._top, name )
          fset = create_fset( self._top, name )
          setattr(self.__class__, name, property(fget, fset) )

    def reset( self ):
      self.cycle( reset=1 )
      self.cycle( reset=1 )

    def cycle( self, clk=0, reset=0 ):
      self._cmodule.cycle( clk, reset, self._top )

    @property
    def ncycles( self ):
      return self._cmodule.ncycles

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

