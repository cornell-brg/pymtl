//========================================================================
// EventQueue.cc
//========================================================================

#include "EventQueue.h"
#include <queue>

typedef void (*FuncPtr)( void );

std::queue < FuncPtr > q;

void init()
{
  // http://stackoverflow.com/a/709161
  std::queue < FuncPtr > empty;
  std::swap( q, empty );
}

void enq( FuncPtr func_ptr )
{
  q.push( func_ptr );
}

FuncPtr deq( void )
{
  FuncPtr item = q.front();
  q.pop();
  return item;
}

int len( void )
{
  return q.size();
}
