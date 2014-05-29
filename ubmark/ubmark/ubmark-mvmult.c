//========================================================================
// ubmark-mvmult
//========================================================================

#include "ubmark.h"
#include "ubmark-mvmult.dat"

//------------------------------------------------------------------------
// mvmult-scalar
//------------------------------------------------------------------------

__attribute__ ((noinline,optimize("unroll-loops")))
void mvmult_scalar( int* resultvector, int* matrix, int* vector, int R, int C )
{
  // TODO: pointer bumps instead of array indexing
  int i; int j; int accum;
  for ( i = 0; i < R; i++ )
  {
    accum = 0;
    for ( j = 0; j < C; j++ ){
      accum += matrix[i*C+j] * vector[j];
      //accum += matrix[i][j] * vector[j];  // TODO: get this to work
    }
    resultvector[i] = accum;
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

    int size = C;
    int dest[size];

    int i;
    for ( i = 0; i < size; i++ )
      dest[i] = 0;

    int temp = 0;

    // warmup
    mvmult_scalar( dest, (int*) matrix, vector, R, C );

    test_stats_on( temp );
    for ( i = 0; i < 1; i++ )
      mvmult_scalar( dest, (int*) matrix, vector, R, C );
    test_stats_off( temp );

    verify_results( dest, ref, size );

    return 0;
}

