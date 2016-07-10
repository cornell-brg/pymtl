#include "Adder_16.h"

void Adder_16::add()
{
  sc_uint<16> A = a.read();
  sc_uint<16> B = b.read();
  c.write(A+B);
}
