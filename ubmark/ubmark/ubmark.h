//========================================================================
// ubmark.h
//========================================================================
// This header contains assembly functions that handle test passes and
// failures, in addition to turning statistics tracking on and off by
// writing the cp0 status register with the mtc0 instruction.

//------------------------------------------------------------------------
// Support for stats
//------------------------------------------------------------------------

inline void test_fail( int temp )
{
  asm( "li %0, 2;"
       "mtc0 %0, $21;"
       "nop;nop;nop;nop;nop;"
       :
       : "r"(temp)
  );
}

inline void test_pass( int temp )
{
  asm( "li %0, 1;"
       "mtc0 %0, $21;"
       "nop;nop;nop;nop;nop;"
       :
       : "r"(temp)
  );
}

inline void test_stats_on( int temp )
{
  asm( "li %0, 1;"
       "mtc0 %0, $10;"
       "nop;nop;nop;nop;nop;"
       :
       : "r"(temp)
  );
}

inline void test_stats_off( int temp )
{
  asm( "li %0, 0;"
       "mtc0 %0, $10;"
       "nop;nop;nop;nop;nop;"
       :
       : "r"(temp)
  );
}

//------------------------------------------------------------------------
// Typedefs
//------------------------------------------------------------------------

typedef unsigned char byte;
typedef unsigned int  uint;

