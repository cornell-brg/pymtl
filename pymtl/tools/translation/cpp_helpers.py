#=======================================================================
# cpp_helpers.py
#=======================================================================

from pymtl                import *
from ...model.signal_lists import PortList
from cffi                 import FFI

# Create position independent code
#cc_src = "g++ -O3 -fPIC -c -o {in}.cc {in}.h {out.o}"
#cc_lib = "g++ -shared -o libCSim.o {out}.so"

#-----------------------------------------------------------------------
# gen_cppsim
#-----------------------------------------------------------------------
def gen_cppsim( clib, cdef ):
  ffi = FFI()
  ffi.cdef( cdef )
  cmodule = ffi.dlopen( clib )
  return cmodule, ffi
  #return wrap( cmodule )

#-----------------------------------------------------------------------
# gen_cdef
#-----------------------------------------------------------------------
# Create the string passed into ffi.cdef
def gen_cdef( cycle_params, top_ports ):
  str_    = '\n'

  str_   += 'typedef struct {\n'
  for name, net, type_ in top_ports:
    str_ += '  {} {};  // {}\n'.format( type_, name[4:], net )
  str_   += '} iface_t;\n\n'

  str_   += 'void cycle({});\n\n'.format('\n'+cycle_params+'\n')

  str_   += 'unsigned int  ncycles;\n'
  return str_

#-----------------------------------------------------------------------
# gen_cheader
#-----------------------------------------------------------------------
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

#-----------------------------------------------------------------------
# gen_pywrapper
#-----------------------------------------------------------------------
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

  #---------------------------------------------------------------------
  # CSimWrapper
  #---------------------------------------------------------------------
  # Inner class for generated python wrapper.
  # TODO: better way?
  class CSimWrapper( object ):

    def __init__( self, cmodule, ffi ):
      #self._model    = model
      self._cmodule  = cmodule
      self._ffi      = ffi
      self._top      = ffi.new("iface_t *")

      #-----------------------------------------------------------------
      # CSimWrapper
      #-----------------------------------------------------------------
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

      #-----------------------------------------------------------------
      # create_fget
      #-----------------------------------------------------------------
      # Utilty method for creating fget
      def create_fget( top, name ):
        return lambda self: getattr( top[0], name )

      #-----------------------------------------------------------------
      # create_fset
      #-----------------------------------------------------------------
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

#-----------------------------------------------------------------------
# create_cpp_py_wrapper
#-----------------------------------------------------------------------
def create_cpp_py_wrapper( model, cdef, lib_file, wrapper_filename ):

  template_filename = '../pymtl/translation/cpp_wrapper.templ.py'

  # translate pymtl      to cpp, cdef
  # compile   cpp        to so
  # create    so,cdef    w  cffi
  # create    pymtl_wrap w  pymtl_cppnames

  port_defs   = []
  set_inputs  = []
  set_outputs = []

  for x in model.get_ports( preserve_hierarchy=True ):
    recurse_port_hierarchy( x, port_defs )

  for x in model.get_inports():
    if x.name in ['clk', 'reset']: continue  # TODO: remove me!
    decl    = "lambda: setattr( s._top, '{}', s.{}.uint() )" \
              .format( x.cpp_name[4:], x.name )
    call    = "s._cffi_update[ s.{} ] = {}".format( x.name, decl )
    set_inputs.append( call )

  for x in model.get_outports():
    decl = "s.{}.value = s._top.{}".format( x.name, x.cpp_name[4:] )
    set_outputs.append( decl )

  # pretty printing
  indent_four = '\n    '
  indent_six  = '\n      '

  # create source
  with open( template_filename, 'r' ) as template, \
       open( wrapper_filename,  'w' ) as output:

    py_src = template.read()
    py_src = py_src.format(
        model_name  = model.class_name,
        cdef        = cdef,
        lib_file    = lib_file,
        port_defs   = indent_four.join( port_defs ),
        set_inputs  = indent_four.join( set_inputs ),
        set_outputs = indent_six .join( set_outputs ),
    )

    output.write( py_src )
    #print py_src

#-----------------------------------------------------------------------
# recurse_port_hierarchy
#-----------------------------------------------------------------------
def recurse_port_hierarchy( p, list_ ):

  if   isinstance( p, PortList ):
    list_.append( "s.{} = [None]*{}".format( p.name, len(p) ) )
    #for child in p.get_ports():
    for child in p._ports:
      recurse_port_hierarchy( child, list_ )

  elif isinstance( p, PortBundle ):
    list_.append( "s.{} = BundleProxy()".format( p.name ) )
    list_.append( "s.{}._ports = []".format( p.name ) )
    for child in p.get_ports():
      recurse_port_hierarchy( child, list_ )
      list_.append( "s.{}._ports.append( s.{} )".format( p.name, child.name ) )
      temp = child.name.split('.')[-1]
      list_.append( "s.{}.name = '{}'".format( child.name, temp ) )

  # TODO: fix msg type
  elif isinstance( p, InPort ):
    list_.append( "s.{} = InPort( {} )".format( p.name, p.nbits ) )

  # TODO: fix msg type
  elif isinstance( p, OutPort ):
    list_.append( "s.{} = OutPort( {} )".format( p.name, p.nbits ) )

