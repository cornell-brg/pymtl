//========================================================================
// ubmark-vvadd
//========================================================================

#include "ubmark.h"
#include "ubmark-vvadd.dat"

//------------------------------------------------------------------------
// vvadd-scalar
//------------------------------------------------------------------------

void vvadd_scalar( int *dest, int *src0, int *src1, int size )
{
  int i;
  for ( i = 0; i < size; i++ )
    *dest++ = *src0++ + *src1++;
}

//------------------------------------------------------------------------
// verify_results
//------------------------------------------------------------------------

void verify_results( int dest[], int ref[], int size )
{
  int temp = 0;
  int i;
  for ( i = 0; i < size; i++ ) {
    if ( !( dest[i] == ref[i] ) ) {
      test_fail( temp );
    }
  }
  test_pass( temp );
}

//------------------------------------------------------------------------
// Test Harness
//------------------------------------------------------------------------

int main( int argc, char* argv[] )
{

    int size = 100;
    int dest[size];

    int i;
    for ( i = 0; i < size; i++ )
      dest[i] = 0;

    int temp = 0;

    test_stats_on( temp );
    vvadd_scalar( dest, src0, src1, size );
    test_stats_off( temp );

    verify_results( dest, ref, size );

    return 0;
}

