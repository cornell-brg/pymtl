#include "obj_dir_{model_name}/V{model_name}.h"
#include "stdio.h"
#include "stdint.h"
#include "verilated.h"
#include "verilated_vcd_c.h"

extern "C" {{
  extern void create_model( void );
  extern void destroy_model( void );
  extern void eval( void );
  extern void trace( void );

  {port_externs}
}}

// Verilator models
V{model_name} * model;
// TODO: make vcd tracing dependent on --dump-vcd flag
//VerilatedVcdC * tfp;
unsigned int trace_time;

// Interface port pointers exposed via CFFI
{port_decls}

// Constructor
void create_model() {{
  model = new V{model_name}();
  //tfp   = new VerilatedVcdC();

  // Enable tracing
  //Verilated::traceEverOn( true );
  trace_time = 0;
  //model->trace( tfp, 99 );
  //tfp->open( "{model_name}.vcd" );

  // Initialize interface pointers
  {port_inits}
}}

// Destructor
void destroy_model() {{
  // TODO: this is probably a memory leak!
  //       But pypy segfaults if uncommented...
  //delete model;
  //tfp->close();
}}

void trace() {{
  trace_time += 1;
  //tfp->dump( trace_time );
}}

void eval() {{
  model->eval();
}}
