#include "systemc.h"

SC_MODULE(RegSC)
{
public:
  sc_in <bool> clk;
  sc_in <bool> rst;
  sc_in <sc_uint<32> > in_;
  sc_out<sc_uint<32> > out;
  
  SC_CTOR(RegSC)
  { 
    SC_CTHREAD(reg, clk.pos());
    
    reset_signal_is(rst, 1);
  }
protected:  
  void reg();
  
public:
  void line_trace(char* str);
};
