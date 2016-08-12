#include "systemc.h"

SC_MODULE(RegIncr_implicit_SC)
{
public:
  sc_in <bool> clk;
  sc_in <bool> reset;
  sc_in <sc_uint<32> > in_;
  sc_out<sc_uint<32> > out;
  
  sc_signal<sc_uint<32> > wire;
  
  SC_CTOR(RegIncr_implicit_SC)
  {
    SC_METHOD(incr);
    sensitive << wire;
    
    SC_CTHREAD(reg, clk.pos());
    
    reset_signal_is(reset, 1);
  }
protected:  
  void incr();
  void reg();
  
public:
  void line_trace(char* str);
};
