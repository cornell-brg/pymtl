#include "systemc.h"
#include "{sc_module_name}.h"

#define SCLINETRACE {sclinetrace}

extern "C"
{{

typedef struct
{{
  {wrap_port_decls}
  
  void *model;
  
}} {sc_module_name}_t;

// Since for now we haven't figured out either a way to totally 
// destroy cffi instance, or to reset some static data structure created 
// by some systemc developer, we reuse the module.

// Here's why I cannot reset the systemc simulation kernel.
// http://stackoverflow.com/questions/37841872/access-some-static-variable-that-are-defined-in-cpp-while-its-class-type-is-als

// Here's why I cannot reset cffi context.
// http://stackoverflow.com/questions/29567200/cleanly-unload-shared-library-and-start-over-with-python-cffi

static {sc_module_name}_t *obj = NULL;
{method_impls}

{sc_module_name}_t* create()
{{
  if (obj)  return obj;
  {new_stmts}
  
  obj = m;
  return m;
}}

void destroy({sc_module_name}_t *obj)
{{
  // Currently we don't reset, and reuse the module by the reset
  // signal, to let it start over again.
  
  // sc_get_curr_simcontext()->reset();
}}

void sim()
{{
  sc_start(1, SC_NS);
}}

#if SCLINETRACE

void line_trace({sc_module_name}_t *obj, char *str)
{{
  {sc_module_name} *model = ({sc_module_name}*) obj->model;
  model->line_trace(str);
}}

#endif

// To link with libsystemc.so we need a dummy sc_main.
int sc_main(int argc, char *argv[]){{return 0;}}
}}


