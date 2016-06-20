#include "systemc.h"
#include "{class_name}.h"

extern "C"
{{

typedef struct
{{
  {port_decls}
  
  void *model;
  
}} {class_name}_t;

// Since for now we haven't figured out either a way to totally 
// destroy cffi instance, or to reset some static data structure by 
// some idiot systemc developer, we reuse the module.

// Here's why I cannot reset the systemc simulation kernel.
// http://stackoverflow.com/questions/37841872/access-some-static-variable-that-are-defined-in-cpp-while-its-class-type-is-als

// Here's why I cannot reset cffi context.
// http://stackoverflow.com/questions/29567200/cleanly-unload-shared-library-and-start-over-with-python-cffi

static {class_name}_t *obj = NULL;
{method_impls}

{class_name}_t* create()
{{
  if (obj)  return obj;
  {new_stmts}
  
  obj = m;
  return m;
}}

void destroy({class_name}_t *obj)
{{
  // Currently we don't reset, and reuse the module by the reset
  // signal, to let it start over again.
  
  // sc_get_curr_simcontext()->reset();
}}

void sim_comb()
{{
  sc_start(0, SC_NS);
}}
void sim_cycle()
{{
  sc_start(1, SC_NS);
}}

}}
