//========================================================================
// ubmark-bin-search
//========================================================================

#include "ubmark.h"
#include "ubmark-bin-search.dat"

//------------------------------------------------------------------------
// bin_search_scalar
//------------------------------------------------------------------------

__attribute__ ((noinline))
void bin_search_scalar( int values[], int keys[], int keys_sz,
                        int kv[], int kv_sz )
{
  int i;
  for ( i = 0; i < keys_sz; i++ ) {

    int key     = keys[i];
    int idx_min = 0;
    int idx_mid = kv_sz/2;
    int idx_max = kv_sz-1;

    int done = 0;
    values[i] = -1;
    do {
      int midkey = kv[idx_mid];

      if ( key == midkey ) {
        values[i] = idx_mid;
        done = 1;
      }

      if ( key > midkey )
        idx_min = idx_mid + 1;
      else if ( key < midkey )
        idx_max = idx_mid - 1;

      idx_mid = ( idx_min + idx_max ) / 2;

    } while ( !done && (idx_min <= idx_max) );

  }
}

//------------------------------------------------------------------------
// verify_results
//------------------------------------------------------------------------

void verify_results( int values[], int ref[], int size )
{
  int temp = 0;
  int i;
  for ( i = 0; i < size; i++ ) {
    if ( !( values[i] == ref[i] ) ) {
      test_fail( i );
    }
  }
  test_pass( temp );
}

//------------------------------------------------------------------------
// Test harness
//------------------------------------------------------------------------

int main( int argc, char* argv[] )
{

  int size = 10;
  int values[size];

  int i;
  for ( i = 0; i < size; i++ )
    values[i] = 0;

  int temp = 0;

  test_stats_on( temp );
  bin_search_scalar( values, keys, size, kv, kv_sz );
  test_stats_off( temp );

  verify_results( values, ref, size );

  return 0;

}

