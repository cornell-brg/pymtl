#include "RegSC.h"

void RegSC::reg()
{
  // reset 
  out.write( 0 ); 
  wait();
  
  while (1)
  {
    out.write( in_.read() );
    wait();
  }
}

#ifndef SYNTHESIS
#include <cstdio>

void RegSC::line_trace(char *str)
{
  char tmp[50];
  sprintf(tmp,"%u > %u",in_.read().to_uint(),out.read().to_uint());
  strcpy(str,tmp);
}
#endif
