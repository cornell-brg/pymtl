#include "systemc.h"

SC_MODULE(Adder_40)
{
public:
  sc_in <sc_uint<40> > a, b;
  sc_out<sc_uint<40> > c;
  
  SC_CTOR(Adder_40)
  {
    SC_METHOD(add);
    sensitive << a << b;
  }
protected:  
  void add();
};
