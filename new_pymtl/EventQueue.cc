//========================================================================
// EventQueue.cc
//========================================================================

#include "EventQueue.h"
#include <vector>
#include <assert.h>
#include <stdio.h>

typedef void (*FuncPtr)( void );

const unsigned int MAX = 1000;

// id_q is a vector of ints.
// This is what we use to track order of evals (each has a unique id)
std::vector < int > id_q ( MAX, -1 );
unsigned int head  = 0;
unsigned int tail  = 0;
unsigned int count = 0;

// func_q is a vector of function pointers.
// On dequeue, we use the id popped off the head of id_q, and use it to
// index into the func_q.  This will give us the function pointer we need
// to call.  We use this as a workaround for the fact that the FuncPtr
// doesn't have an id attached to it.  (Another approach would be to store
// a struct with FuncPtr + int id).
std::vector < FuncPtr > func_q ( MAX, NULL );

void init()
{
  // http://stackoverflow.com/a/709161
  std::vector < FuncPtr > empty_func ( MAX, NULL );
  std::vector < int >     empty_id   ( MAX, -1   );
  std::swap( func_q, empty_func );
  std::swap( id_q,   empty_id   );
  head  = 0;
  tail  = 0;
  count = 0;
}

void enq( FuncPtr func_ptr, unsigned int id )
{
  assert( count < MAX );
  //printf("\nENQ id: %d, func: %p, func_q: %p, id_q %d\n", id, func_ptr, func_q[id], id_q[tail] );
  //printf("in q? %b", func_q[id] == NULL );
  if ( func_q[ id ] == NULL ) {
    func_q[ id ] = func_ptr;
    id_q  [tail] = id;
    tail = (tail + 1) % MAX;
    count++;
  }
}

FuncPtr eval( void )
{
  assert( count > 0 );
  int id       = id_q  [ head ];
  //printf("\nDEQ id: %d, func: %p, id_q %d\n", id, func_q[ id ], id_q[tail] );
  FuncPtr item = func_q[ id ];
  head = (head + 1) % MAX;
  count--;
  item();
  func_q[ id ] = NULL;
}

int len( void )
{
  return count;
}
