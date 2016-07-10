#include "Adder_100.h"

void Adder_100::add()
{
  sc_biguint<100> A = a.read();
  sc_biguint<100> B = b.read();
  
  c.write(A+B);
}
