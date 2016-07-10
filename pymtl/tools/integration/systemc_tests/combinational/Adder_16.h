#include "systemc.h"

SC_MODULE(Adder_16)
{
public:
  sc_in <sc_uint<16> > a, b;
  sc_out<sc_uint<16> > c;
  
  SC_CTOR(Adder_16)
  {
    SC_METHOD(add);
    sensitive << a << b;
  }
protected:  
  void add();
};
