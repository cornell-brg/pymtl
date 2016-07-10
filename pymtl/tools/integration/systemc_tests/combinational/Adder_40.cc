#include "Adder_40.h"

void Adder_40::add()
{
  sc_uint<40> A = a.read();
  sc_uint<40> B = b.read();
  
  c.write(A+B);
}
