#=========================================================================
# EventQueue.py
#=========================================================================

from cffi import FFI
ffi = FFI()

# Header file

ffi.cdef("""
  typedef  void (*FuncPtr)( void );
  void     init ( void     );
  void     enq  ( FuncPtr func_ptr, unsigned int id );
  FuncPtr  eval ( void     );
  int      len  ( void     );
""")

# Library loading

# Open the dynamic shared library.
try:
  cpp_queue = ffi.dlopen( './libEventQueue.so' )

# Can't find the library!
except OSError:

  # Try building it...
  import subprocess
  make_cmd = "make -f ../new_pymtl/Make_cffi"
  subprocess.call( make_cmd.split(' ') )

  # Then re-loading it.
  try:
    cpp_queue = ffi.dlopen( './libEventQueue.so' )

  # Still not working!  Throw an error.
  except OSError as e:
    raise OSError( "{}\n\n{}\n{}\n\n    {}\n".format( e,
                   "You probably didn't build the C components!",
                   "Try running the following command first:",
                   make_cmd ))


# Utility function for creating new C++ queue instance

def new_cpp_queue():
  cpp_queue.init()
  return cpp_queue

# Utility function for creating c callbacks

def cpp_callback( func ):
  return ffi.callback( 'FuncPtr', func )

