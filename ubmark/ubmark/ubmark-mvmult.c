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

////__attribute__ ((noinline))
//void mvmult_coprocessor( int*  resultvector, int** matrix, int*  vector,
//                         int R, int C, int nlanes )
//{
//  int  size    = C;
//  for( int i = 0; i < R; i+=nlanes ) {
//    int* r_baddr = &(matrix[i][0]);
//    int* v_baddr = &(vector[0]);
//    int* d_baddr = &(resultvector[i]);
//    //std::cout << "addr: " << &(matrix[i  ][0]) << "value: " << matrix[i  ][0] << std::endl;
//    //std::cout << "addr: " << &(matrix[i+1][0]) << "value: " << matrix[i+1][0] << std::endl;
//    // TODO: add native code
//    #ifdef _MIPS_ARCH_MAVEN
//    // TODO: left shift by two in order to avoid unaligned branch warning,
//    //       but processor still sees the unshifted version...
//    __asm__ __volatile__ ( "xloop %0, %1;" : : "r"(size),    "i"(1<<2) : "memory" );
//    __asm__ __volatile__ ( "xloop %0, %1;" : : "r"(r_baddr), "i"(2<<2) : "memory" );
//    __asm__ __volatile__ ( "xloop %0, %1;" : : "r"(v_baddr), "i"(3<<2) : "memory" );
//    __asm__ __volatile__ ( "xloop %0, %1;" : : "r"(d_baddr), "i"(4<<2) : "memory" );
//    __asm__ __volatile__ ( "mtvps $0, $0;" : :                         :          );
//    #endif
//  }
//}


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
    mvmult_scalar( dest, (int*) matrix, vector, R, C );
    test_stats_off( temp );

    verify_results( dest, ref, size );

    return 0;
}

