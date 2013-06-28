//========================================================================
// EventQueue.h
//========================================================================
// We use an extern "C" wrapper so that we can call this from Python
// using cffi.

#ifndef EVENTQUEUE_H
#define EVENTQUEUE_H

extern "C" {

  typedef  void    (*FuncPtr)( void );
  extern   void    enq       ( FuncPtr func_ptr );
  extern   FuncPtr deq       ( void );
  extern   int     len       ( void );

}

#endif

