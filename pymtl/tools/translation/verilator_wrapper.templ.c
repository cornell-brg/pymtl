//======================================================================
// V{model_name}_v.cpp
//======================================================================
// This wrapper exposes a C interface to CFFI so that a
// Verilator-generated C++ model can be driven from Python.
//

#include "obj_dir_{model_name}/V{model_name}.h"
#include "stdio.h"
#include "stdint.h"
#include "verilated.h"
#include "verilated_vcd_c.h"

// set to true when VCD tracing is enabled in Verilator
#define DUMP_VCD {dump_vcd}

//----------------------------------------------------------------------
// CFFI Interface
//----------------------------------------------------------------------

// simulation methods and model interface ports exposed to CFFI
extern "C" {{
  typedef struct {{

    // Exposed port interface
    {port_externs}

    // Verilator model
    void * model;

  }} V{model_name}_t;

  V{model_name}_t * create_model( const char * );
  void destroy_model( V{model_name}_t *);
  void eval( V{model_name}_t * );

}}

//----------------------------------------------------------------------
// Private data
//----------------------------------------------------------------------

#if DUMP_VCD
// VCD tracing helpers
VerilatedVcdC * tfp;
unsigned int  trace_time;
unsigned char prev_clk;
#endif

//----------------------------------------------------------------------
// create_model()
//----------------------------------------------------------------------
// Construct a new verilator simulation, initialize interface signals
// exposed via CFFI, and setup VCD tracing if enabled.
//
V{model_name}_t * create_model( const char *vcd_filename ) {{

  V{model_name}_t * m;
  V{model_name}   * model;

  m     = (V{model_name}_t *) malloc( sizeof(V{model_name}_t) );
  model = new V{model_name}();

  m->model = (void *) model;

#if DUMP_VCD
  // enable tracing
  Verilated::traceEverOn( true );
  tfp = new VerilatedVcdC();
  model->trace( tfp, 99 );
  tfp->spTrace()->set_time_resolution( "{vcd_timescale}" );
  tfp->open( vcd_filename );
  trace_time = 0;
  prev_clk   = 0;
#endif

  // initialize exposed model interface pointers
  {port_inits}

  return m;
}}

//----------------------------------------------------------------------
// destroy_model()
//----------------------------------------------------------------------
// Finalize the Verilator simulation, close files, call destructors.
//
void destroy_model( V{model_name}_t * m ) {{

  V{model_name} * model = (V{model_name} *) m->model;

  // finalize verilator simulation
  model->final();

#if DUMP_VCD
  // close the vcd file
  printf("DESTROYING %d\n", trace_time );
  tfp->close();
#endif

  // TODO: this is probably a memory leak!
  //       But pypy segfaults if uncommented...
  //delete model;

}}

//----------------------------------------------------------------------
// eval()
//----------------------------------------------------------------------
// Simulate one time-step in the Verilated model.
//
void eval( V{model_name}_t * m ) {{

  V{model_name} * model = (V{model_name} *) m->model;

  // evaluate one time step
  model->eval();

#if DUMP_VCD

  // update simulation time only on clock toggle
  if (prev_clk != model->clk) {{ trace_time += 50; }}
  prev_clk = model->clk;

  // dump current signal values
  tfp->dump( trace_time );
  tfp->flush();
#endif

}}
