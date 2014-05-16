//========================================================================
// ubmark-mvmult-cp2
//========================================================================

#include "ubmark.h"
#include "ubmark-mvmult.dat"

//------------------------------------------------------------------------
// mvmult-cp2
//------------------------------------------------------------------------

__attribute__ ((noinline))
void mvmult_cp2( int* resultvector, int* matrix, int* vector,
                 int R, int C, int nlanes )
{
  int i    = 0;
  int go   = 1;
  int size = C;

  for( i = 0; i < R; i+=nlanes ) {
    int* r_baddr = &(matrix[i*C]);
    int* v_baddr = &(vector[0]);
    int* d_baddr = &(resultvector[i]);
    // TODO: add native code
    #ifdef _MIPS_ARCH_MAVEN
    // TODO: left shift by two in order to avoid unaligned branch warning,
    //       but processor still sees the unshifted version...
    __asm__ __volatile__ ( "mtc2 %0, $1;" : : "r"(size)    : "memory" );
    __asm__ __volatile__ ( "mtc2 %0, $2;" : : "r"(r_baddr) : "memory" );
    __asm__ __volatile__ ( "mtc2 %0, $3;" : : "r"(v_baddr) : "memory" );
    __asm__ __volatile__ ( "mtc2 %0, $4;" : : "r"(d_baddr) : "memory" );
    __asm__ __volatile__ ( "mtc2 %0, $0;" : : "r"(go)      : "memory" );
    #endif
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

    test_stats_on( temp );
    mvmult_cp2( dest, (int*) matrix, vector, R, C, 1 );
    test_stats_off( temp );

    verify_results( dest, ref, size );

    return 0;
}

