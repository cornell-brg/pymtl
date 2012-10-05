//========================================================================
// ubmark-masked-filter
//========================================================================

#include "ubmark.h"
#include "ubmark-masked-filter.dat"

//------------------------------------------------------------------------
// global coeffient values
//------------------------------------------------------------------------

uint g_coeff[] = { 8, 6 };

//------------------------------------------------------------------------
// masked_filter_scalar
//------------------------------------------------------------------------

__attribute__ ((noinline))
void masked_filter_scalar( uint dest[], uint mask[], uint src[],
                           int nrows, int ncols, uint coeff[] )
{
  uint coeff0 = coeff[0];
  uint coeff1 = coeff[1];
  uint norm = coeff[0] + 4*coeff[1];
  int ridx;
  int cidx;
  for ( ridx = 1; ridx < nrows-1; ridx++ ) {
    for ( cidx = 1; cidx < ncols-1; cidx++ ) {
      if ( mask[ ridx*ncols + cidx ] != 0 ) {
        uint out0 = ( src[ (ridx-1)*ncols + cidx     ] * coeff1 );
        uint out1 = ( src[ ridx*ncols     + (cidx-1) ] * coeff1 );
        uint out2 = ( src[ ridx*ncols     + cidx     ] * coeff0 );
        uint out3 = ( src[ ridx*ncols     + (cidx+1) ] * coeff1 );
        uint out4 = ( src[ (ridx+1)*ncols + cidx     ] * coeff1 );
        uint out  = out0 + out1 + out2 + out3 + out4;
        dest[ ridx*ncols + cidx ] = (byte)(out/norm);
      }
      else
        dest[ ridx*ncols + cidx ] = src[ ridx*ncols + cidx ];
    }
  }
}

//------------------------------------------------------------------------
// verify_results
//------------------------------------------------------------------------

void verify_results( uint dest[], uint ref[], int size )
{
  int temp = 0;
  int i;
  for ( i = 0; i < size*size; i++ ) {
    if ( !( dest[i] == ref[i] ) ) {
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

    int size = 20;
    uint dest[size*size];

    int i;
    for ( i = 0; i < size*size; i++ )
      dest[i] = 0;

    int temp = 0;

    test_stats_on( temp );
    masked_filter_scalar( dest, mask, src, size, size, g_coeff );
    test_stats_off( temp );

    verify_results( dest, ref, size );

    return 0;

}

