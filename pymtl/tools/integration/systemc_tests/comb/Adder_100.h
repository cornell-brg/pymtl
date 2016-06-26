#include "systemc.h"

SC_MODULE(Adder_100)
{
public:
  sc_in <sc_biguint<100> > a, b;
  sc_out<sc_biguint<100> > c;
  
  SC_CTOR(Adder_100)
  {
    SC_METHOD(add);
    sensitive << a << b;
  }
protected:  
  void add();
};
