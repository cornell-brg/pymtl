#=========================================================================
# SimulationMetrics.py
#=========================================================================

from __future__ import print_function

import pickle

#-------------------------------------------------------------------------
# SimulationMetrics
#-------------------------------------------------------------------------
# Utility class for storing various SimulationTool metrics. Useful for
# gaining insight into simulator performace and determining the simulation
# efficiency of hardware model implementations.
class SimulationMetrics( object ):

  #-----------------------------------------------------------------------
  # __init__
  #-----------------------------------------------------------------------
  def __init__( self ):
    self._ncycles                                = 0
    self._pre_tick                               = True
    self.num_modules                             = 0
    self.num_tick_blocks                         = 0
    self.num_posedge_clk_blocks                  = 0
    self.num_combinational_blocks                = 0
    self.num_slice_blocks                        = 0
    self.input_add_events_per_cycle              = [ 0 ]
    self.clock_add_events_per_cycle              = [ 0 ]
    self.input_add_callbk_per_cycle              = [ 0 ]
    self.clock_add_callbk_per_cycle              = [ 0 ]
    self.input_comb_evals_per_cycle              = [ 0 ]
    self.clock_comb_evals_per_cycle              = [ 0 ]
    self.slice_comb_evals_per_cycle              = [ 0 ]
    self.redun_comb_evals_per_cycle              = [ 0 ]
    self.is_slice                                = dict()
    self.has_run                                 = dict()

  #-----------------------------------------------------------------------
  # comb_evals_per_cycle
  #-----------------------------------------------------------------------
  @property
  def comb_evals_per_cycle( self ):
    return [ x+y for x,y in zip( self.input_comb_evals_per_cycle,
                                 self.clock_comb_evals_per_cycle ) ]

  #-----------------------------------------------------------------------
  # add_events_per_cycle
  #-----------------------------------------------------------------------
  @property
  def add_events_per_cycle( self ):
    return [ x+y for x,y in zip( self.input_add_events_per_cycle,
                                 self.clock_add_events_per_cycle ) ]

  #-----------------------------------------------------------------------
  # reg_model
  #-----------------------------------------------------------------------
  # Register a model in the design.
  def reg_model( self, model ):
    self.num_modules              += 1
    self.num_tick_blocks          += len( model.get_tick_blocks() )
    self.num_posedge_clk_blocks   += len( model.get_posedge_clk_blocks() )
    self.num_combinational_blocks += len( model.get_combinational_blocks() )

  #-----------------------------------------------------------------------
  # reg_eval
  #-----------------------------------------------------------------------
  # Register an eval block in the design.
  def reg_eval( self, eval, is_slice = False ):
    self.has_run [ eval ] = False
    self.is_slice[ eval ] = is_slice
    if is_slice:
      self.num_slice_blocks += 1

  #-----------------------------------------------------------------------
  # incr_metrics_cycle
  #-----------------------------------------------------------------------
  # Should be called at the end of each simulation cycle. Initializes data
  # structure storage to collect data for the next simulation cycle.
  def incr_metrics_cycle( self ):
    self._pre_tick                   = True
    self._ncycles                   += 1
    self.input_add_events_per_cycle += [ 0 ]
    self.clock_add_events_per_cycle += [ 0 ]
    self.input_add_callbk_per_cycle += [ 0 ]
    self.clock_add_callbk_per_cycle += [ 0 ]
    self.input_comb_evals_per_cycle += [ 0 ]
    self.clock_comb_evals_per_cycle += [ 0 ]
    self.slice_comb_evals_per_cycle += [ 0 ]
    self.redun_comb_evals_per_cycle += [ 0 ]
    for key in self.has_run:
      self.has_run[ key ] = False

  #-----------------------------------------------------------------------
  # start_tick
  #-----------------------------------------------------------------------
  # Should be called before sequential logic blocks are executed.  Allows
  # collection of unique metrics for each phase of eval execution.
  def start_tick( self ):
    self._pre_tick                   = False

  #-----------------------------------------------------------------------
  # incr_add_events
  #-----------------------------------------------------------------------
  # Increment the number of times add_event() was called.
  def incr_add_events( self ):
    if self._pre_tick:
      self.input_add_events_per_cycle[ self._ncycles ] += 1
    else:
      self.clock_add_events_per_cycle[ self._ncycles ] += 1

  #-----------------------------------------------------------------------
  # incr_add_events
  #-----------------------------------------------------------------------
  # Increment the number of callbacks we attempted to place on the event
  # queue.
  def incr_add_callbk( self ):
    if self._pre_tick:
      self.input_add_callbk_per_cycle[ self._ncycles ] += 1
    else:
      self.clock_add_callbk_per_cycle[ self._ncycles ] += 1

  #-----------------------------------------------------------------------
  # incr_comb_evals
  #-----------------------------------------------------------------------
  # Increment the number of evals we actually executed.
  def incr_comb_evals( self, eval ):
    if self._pre_tick:
      self.input_comb_evals_per_cycle[ self._ncycles ] += 1
    else:
      self.clock_comb_evals_per_cycle[ self._ncycles ] += 1

    if   self.has_run[ eval ]:
      self.redun_comb_evals_per_cycle[ self._ncycles ] += 1
    else:
      self.has_run[ eval ] = True

    if   self.is_slice[ eval ]:
      self.slice_comb_evals_per_cycle[ self._ncycles ] += 1

  #-----------------------------------------------------------------------
  # print_metrics
  #-----------------------------------------------------------------------
  # Print metrics to the commandline.
  def print_metrics( self, detailed = True ):
    print("-"*72)
    print("Simulation Metrics")
    print("-"*72)
    print()
    print("ncycles:               {:4}".format(self._ncycles                ))
    print("modules:               {:4}".format(self.num_modules             ))
    print("@tick blocks:          {:4}".format(self.num_tick_blocks         ))
    print("@posedge_clk blocks:   {:4}".format(self.num_posedge_clk_blocks  ))
    print("@combinational blocks: {:4}".format(self.num_combinational_blocks))
    print("slice blocks:          {:4}".format(self.num_slice_blocks        ))
    print("-"*72)
    if not detailed:
      return
    print()
    print("          pre-tick          post-tick         other       ")
    print("cycle     adde  clbk  eval  adde  clbk  eval  slice  redun")
    print("--------  ----  ----  ----  ----  ----  ----  -----  -----")
    for i in range( self._ncycles ):
      print("{:8}  {:4}  {:4}  {:4}  {:4}  {:4}  {:4}  {:5}  {:5}".format(
                   i, self.input_add_events_per_cycle[ i ],
                      self.input_add_callbk_per_cycle[ i ],
                      self.input_comb_evals_per_cycle[ i ],
                      self.clock_add_events_per_cycle[ i ],
                      self.clock_add_callbk_per_cycle[ i ],
                      self.clock_comb_evals_per_cycle[ i ],
                      self.slice_comb_evals_per_cycle[ i ],
                      self.redun_comb_evals_per_cycle[ i ],
                   ))
    print("-"*72)

  #-----------------------------------------------------------------------
  # pickle_metrics
  #-----------------------------------------------------------------------
  # Pickle metrics to a file.  Useful for loading in Python later for
  # for creating matplotlib plots.
  def pickle_metrics( self, filename ):
    del self.is_slice
    del self.has_run
    pickle.dump( self, open( filename, 'wb' ) )

#-------------------------------------------------------------------------
# DummyMetrics
#-------------------------------------------------------------------------
# Dummy class which provides the interface of the SimulationMetrics
# metrics collection class, but doesn't actually collect anything metrics.
# This is used as a swap in replacement when collection is disabled so
# developers don't have to worry about adding a check to disable each
# call to SimulationMetrics methods.
class DummyMetrics( object ):

  def reg_model( self, model ): pass
  def reg_eval( self, eval, is_slice = False ): pass
  def incr_metrics_cycle( self ): pass
  def start_tick( self ): pass
  def incr_add_events( self ): pass
  def incr_add_callbk( self ): pass
  def incr_comb_evals( self, eval ): pass
