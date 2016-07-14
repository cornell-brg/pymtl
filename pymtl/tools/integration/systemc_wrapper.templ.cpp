#include "systemc.h"
#include "{sc_module_name}.h"

#define SCLINETRACE {sclinetrace}

extern "C"
{{

typedef struct
{{
  {wrap_port_decls}
  
  void *context;
  void *model;
  
}} {sc_module_name}_t;

// June 22, 2016
// Since for now we haven't figured out either a way to totally 
// destroy cffi instance, or to reset some static data structure created 
// by some systemc developer, we reuse the module.

//static {sc_module_name}_t *obj = NULL;

// Here's why I cannot reset the systemc simulation kernel.
// http://stackoverflow.com/questions/37841872/access-some-static-variable-that-are-defined-in-cpp-while-its-class-type-is-als

// Here's why I cannot reset cffi context.
// http://stackoverflow.com/questions/29567200/cleanly-unload-shared-library-and-start-over-with-python-cffi

{method_impls}

{sc_module_name}_t* create()
{{
  {new_stmts}
  
  return m;
}}

void destroy({sc_module_name}_t *obj)
{{
  // Currently we can only remove a simcontext by assign the current to be NULL
  // Also this is not perfect, since we have to manually call it.
  // http://forums.accellera.org/topic/2273-problem-with-re-instatiation-of-modules/
  //sc_curr_simcontext = 0;
  //sc_default_global_context = 0;
  
  // Or we could reset the sim_context since it's basically the same thing but
  // avoids some memory leak
  //sc_get_curr_simcontext()->reset();
  
  // July 7, 2016
  // I found the bug which prevents me from destroying the simcontext.
  // Then I posted it to the SystemC forum.
  // http://forums.accellera.org/topic/5563-bug-in-sc-resetreconcile-resets/
  // People have recognized what I found as a bug :) Yay!  
  
  // July 11, 2016
  // Now I decide to create one sim context for each module. So delete here.
  // Also notice that creating one sim context for each model could guarantee
  // that the py.test still moves on when the destroy is not called (assert failed somewhere)
  
  {delete_stmts}
  sc_simcontext *context = static_cast<sc_simcontext*>(obj->context);
  delete context;
}}

void sim({sc_module_name}_t *obj)
{{
  sc_curr_simcontext = static_cast<sc_simcontext*>(obj->context);
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


