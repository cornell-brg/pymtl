#include "obj_dir_{model_name}/V{model_name}.h"
#include "stdio.h"
#include "stdint.h"
#include "verilated.h"
#include "verilated_vcd_c.h"

#define DUMP_VCD {dump_vcd}

extern "C" {{
  extern void create_model( void );
  extern void destroy_model( void );
  extern void eval( void );
  extern void trace( void );

  {port_externs}
}}

// Verilator models
V{model_name} * model;

#if DUMP_VCD
VerilatedVcdC * tfp;
unsigned int trace_time;
#endif

// Interface port pointers exposed via CFFI
{port_decls}

// Constructor
void create_model() {{
  model = new V{model_name}();

  printf("CREATING OUT\n");
#if DUMP_VCD
  printf("CREATING IN\n");
  // Enable tracing
  Verilated::traceEverOn( true );
  tfp = new VerilatedVcdC();
  model->trace( tfp, 99 );
  tfp->open( "{model_name}.vcd" );
  trace_time = 0;
#endif

  // Initialize interface pointers
  {port_inits}
}}

// Destructor
void destroy_model() {{
  // TODO: this is probably a memory leak!
  //       But pypy segfaults if uncommented...
  //delete model;
#if DUMP_VCD
  printf("DESTROYING %d\n", trace_time );
  tfp->close();
#endif
}}

void eval() {{
  model->eval();
}}

void trace() {{
#if DUMP_VCD
  trace_time += 5;
  printf("DUMPING %d\n", trace_time );
  tfp->dump( trace_time );
#endif
}}
