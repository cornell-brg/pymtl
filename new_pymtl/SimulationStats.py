import pickle

class SimulationStats( object ):

  def __init__( self ):
    self._ncycles                                = 0
    self._pre_tick                               = True
    self.num_modules                             = 0
    self.num_tick_blocks                         = 0
    self.num_posedge_clk_blocks                  = 0
    self.num_combinational_blocks                = 0
    self.input_add_events_per_cycle              = [ 0 ]
    self.clock_add_events_per_cycle              = [ 0 ]
    self.input_add_callbk_per_cycle              = [ 0 ]
    self.clock_add_callbk_per_cycle              = [ 0 ]
    self.input_comb_evals_per_cycle              = [ 0 ]
    self.clock_comb_evals_per_cycle              = [ 0 ]

  @property
  def comb_evals_per_cycle( self ):
    return [ x+y for x,y in zip( self.input_comb_evals_per_cycle,
                                 self.clock_comb_evals_per_cycle ) ]

  @property
  def add_events_per_cycle( self ):
    return [ x+y for x,y in zip( self.input_add_events_per_cycle,
                                 self.clock_add_events_per_cycle ) ]

  def incr_stats_cycle( self ):
    self._pre_tick                   = True
    self._ncycles                   += 1
    self.input_add_events_per_cycle += [ 0 ]
    self.clock_add_events_per_cycle += [ 0 ]
    self.input_add_callbk_per_cycle += [ 0 ]
    self.clock_add_callbk_per_cycle += [ 0 ]
    self.input_comb_evals_per_cycle += [ 0 ]
    self.clock_comb_evals_per_cycle += [ 0 ]

  def start_tick( self ):
    self._pre_tick                   = False

  def incr_add_events( self ):
    if self._pre_tick:
      self.input_add_events_per_cycle[ self._ncycles ] += 1
    else:
      self.clock_add_events_per_cycle[ self._ncycles ] += 1

  def incr_add_callbk( self ):
    if self._pre_tick:
      self.input_add_callbk_per_cycle[ self._ncycles ] += 1
    else:
      self.clock_add_callbk_per_cycle[ self._ncycles ] += 1

  def incr_comb_evals( self ):
    if self._pre_tick:
      self.input_comb_evals_per_cycle[ self._ncycles ] += 1
    else:
      self.clock_comb_evals_per_cycle[ self._ncycles ] += 1

  def print_stats( self, detailed=True ):
    print "-"*72
    print "Simulator Statistics"
    print "-"*72
    print
    print "ncycles:               {:4}".format( self._ncycles                 )
    print "modules:               {:4}".format( self.num_modules              )
    print "@tick blocks:          {:4}".format( self.num_tick_blocks          )
    print "@posedge_clk blocks:   {:4}".format( self.num_posedge_clk_blocks   )
    print "@combinational blocks: {:4}".format( self.num_combinational_blocks )
    if not detailed:
      return
    print
    print "          pre-tick          post-tick"
    print "cycle     adde  clbk  eval  adde  clbk  eval"
    print "--------  ----  ----  ----  ----  ----  ----"
    for i in range( self._ncycles ):
      print "{:8}  {:4}  {:4}  {:4}  {:4}  {:4}  {:4}".format( i,
                                                   self.input_add_events_per_cycle[ i ],
                                                   self.input_add_callbk_per_cycle[ i ],
                                                   self.input_comb_evals_per_cycle[ i ],
                                                   self.clock_add_events_per_cycle[ i ],
                                                   self.clock_add_callbk_per_cycle[ i ],
                                                   self.clock_comb_evals_per_cycle[ i ] )

  def pickle_stats( self, filename ):
    pickle.dump( self, open( filename, 'wb' ) )
