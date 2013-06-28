#=========================================================================
# EventQueue.py
#=========================================================================

from cffi import FFI
ffi = FFI()

# Header file

ffi.cdef("""
  typedef  void (*FuncPtr)( void );
  void     enq  ( FuncPtr func_ptr );
  FuncPtr  deq  ( void     );
  int      len  ( void     );
""")

# Open the dynamic shared library

try:
  cpp_queue = ffi.dlopen( './libEventQueue.so' )
except OSError as e:
  raise OSError( "{}\n\n{}\n{}\n\n{}\n".format( e,
                 "You probably didn't build the C components!",
                 "Try running the following command first:",
                 "    make -f ../new_pymtl/Make_cffi" )
               )

def cpp_callback( func ):
  return ffi.callback( 'FuncPtr', func )

