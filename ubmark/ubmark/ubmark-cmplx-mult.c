//========================================================================
// ubmark-cmlpx-mult
//========================================================================

#include "ubmark.h"
#include "ubmark-cmplx-mult.dat"

//------------------------------------------------------------------------
// cmplx-mult-scalar
//------------------------------------------------------------------------

void cmplx_mult_scalar( int dest[], int src0[],
                        int src1[], int size )
{
  int i;
  for ( i = 0; i < size; i++ ) {
    dest[i*2]   = (src0[i*2] * src1[i*2]) - (src0[i*2+1] * src1[i*2+1]);
    dest[i*2+1] = (src0[i*2] * src1[i*2+1]) + (src0[i*2+1] * src1[i*2]);
  }
}

//------------------------------------------------------------------------
// verify_results
//------------------------------------------------------------------------

void verify_results( int dest[], int ref[], int size )
{
  int temp = 0;
  int i;
  for ( i = 0; i < size; i++ ) {
    if ( !( ( dest[i*2] == ref[i*2] ) && ( dest[i*2+1] == ref[i*2+1] ) ) ) {
      test_fail( temp );
    }
  }
  test_pass( temp );
}

//------------------------------------------------------------------------
// Test harness
//------------------------------------------------------------------------

int main( int argc, char* argv[] )
{

    int size = 100;
    int dest[size*2];

    int i;
    for ( i = 0; i < size*2; i++ )
      dest[i] = 0;

    int temp = 0;

    test_stats_on( temp );
    cmplx_mult_scalar( dest, src0, src1, size );
    test_stats_off( temp );

    verify_results( dest, ref, size );

    return 0;

}

