#include "IncrSC.h"

void IncrSC::incr()
{
  out.write( in_.read() + 1 );
}

#ifndef SYNTHESIS
#include <cstdio>

void IncrSC::line_trace(char *str)
{
  char tmp[50];
  sprintf(tmp,"%u > %u",in_.read().to_uint(),out.read().to_uint());
  strcpy(str,tmp);
}
#endif
