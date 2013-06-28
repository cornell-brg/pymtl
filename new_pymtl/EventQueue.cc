//========================================================================
// EventQueue.cc
//========================================================================

#include "EventQueue.h"
#include <queue>
#include <list>

typedef void (*FuncPtr)( void );

std::queue < FuncPtr, std::list<FuncPtr> > queue;

void enq( FuncPtr func_ptr )
{
  queue.push( func_ptr );
}

FuncPtr deq( void )
{
  FuncPtr item = queue.front();
  queue.pop();
  return item;
}

int len( void )
{
  return queue.size();
}
