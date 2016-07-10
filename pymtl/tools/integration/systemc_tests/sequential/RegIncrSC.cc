#include "RegIncrSC.h"

void RegIncrSC::incr()
{
  // combinational incrementer
  out.write( wire.read() + 1 );
}

void RegIncrSC::reg()
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

void RegIncrSC::line_trace(char *str)
{
  char tmp[50];
  sprintf(tmp,"in=%u out=%u",in_.read().to_uint(),out.read().to_uint());
  strcpy(str,tmp);
}
#endif
