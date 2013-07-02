//========================================================================
// EventQueue.cc
//========================================================================

#include "EventQueue.h"
#include <vector>
#include <assert.h>
#include <stdio.h>

typedef void (*FuncPtr)( void );

const unsigned int MAX = 1000;

std::vector < FuncPtr > q ( MAX, NULL );
unsigned int head  = 0;
unsigned int tail  = 0;
unsigned int count = 0;

std::vector < bool > in_q ( MAX, 0 );

void init()
{
  // http://stackoverflow.com/a/709161
  std::vector < FuncPtr > empty ( MAX, NULL );
  std::swap( q, empty );
  head  = 0;
  tail  = 0;
  count = 0;
}

void enq( FuncPtr func_ptr, unsigned int id )
{
  assert( count < MAX );
  if ( not in_q[ id ] ) {
    q[tail] = func_ptr;
    tail = (tail + 1) % MAX;
    count++;
  }
}

FuncPtr deq( void )
{
  assert( count > 0 );
  FuncPtr item = q[head];
  head = (head + 1) % MAX;
  count--;
  return item;
}

int len( void )
{
  return count;
}
