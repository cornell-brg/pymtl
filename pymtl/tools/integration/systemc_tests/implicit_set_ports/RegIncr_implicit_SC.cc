#include "RegIncr_implicit_SC.h"

void RegIncr_implicit_SC::incr()
{
  // combinational incrementer
  out.write( wire.read() + 1 );
}

void RegIncr_implicit_SC::reg()
{
  // reset 
  wire.write( 0 ); 
  wait();
  
  while (1)
  {
    wire.write( in_.read() );
    wait();
  }
}

#ifndef SYNTHESIS
#include <cstdio>

void RegIncr_implicit_SC::line_trace(char *str)
{
  char tmp[50];
  sprintf(tmp,"in=%u out=%u",in_.read().to_uint(),out.read().to_uint());
  strcpy(str,tmp);
}
#endif
