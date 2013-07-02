//========================================================================
// EventQueue.h
//========================================================================
// We use an extern "C" wrapper so that we can call this from Python
// using cffi.

#ifndef EVENTQUEUE_H
#define EVENTQUEUE_H

extern "C" {

  typedef  void    (*FuncPtr)( void );
  extern   void    init      ( void );
  extern   void    enq       ( FuncPtr func_ptr, unsigned int id );
  extern   FuncPtr eval      ( void );
  extern   int     len       ( void );

}

#endif

