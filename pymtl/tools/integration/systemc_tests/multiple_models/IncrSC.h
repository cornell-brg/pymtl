#include "systemc.h"

SC_MODULE(IncrSC)
{
public:
  sc_in <sc_uint<32> > in_;
  sc_out<sc_uint<32> > out;
  
  SC_CTOR(IncrSC)
  {
    SC_METHOD(incr);
    sensitive << in_;
  }
  
protected:  
  void incr();
  
public:
  void line_trace(char* str);
};
