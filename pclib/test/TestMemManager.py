#=========================================================================
# TestMemManager
#=========================================================================
# This class implements TestMemManager.

from pymtl import *

class TestMemManager (Model):

  #-----------------------------------------------------------------------
  # Constructor
  #-----------------------------------------------------------------------

  def __init__( s, mem, sparse_mem_img ):

    # Interface Ports

    s.mem_status = InPort  ( 1 )

    s.mem_go     = OutPort ( 1 )
    s.done       = OutPort ( 1 )

    # Test Memory load done signal

    s.load_done  = 0
    s.curr_label = 0

    # test memory pointer
    s.mem = mem

    # sparse memory image pointer
    s.sparse_mem_img = sparse_mem_img

    # State

    s.STATE_LOAD = 0
    s.STATE_RUN  = 1
    s.STATE_DONE = 2

    s.state      = s.STATE_LOAD

    #-----------------------------------------------------------------------
    # Tick
    #-----------------------------------------------------------------------

    @s.posedge_clk
    def tick():

      if s.reset.value:
        pass

      else:
        # start loading the memory after reset

        if s.state == s.STATE_LOAD:

          s.load_done = ( s.curr_label  == s.sparse_mem_img.num_labels() )

          # load memory label
          if not s.load_done:

            s.mem.load_memory( s.sparse_mem_img.read_label( s.curr_label ) )
            s.curr_label += 1

          # tranistion out of LOAD
          else:

            s.state        = s.STATE_RUN
            s.mem_go.next = 1

        # wait for processor to complete running

        if s.state == s.STATE_RUN:

          # transition out of RUN

          if s.mem_status.value == 1:
            s.mem_go.next = 0
            s.done.next    = 1
            s.state        = s.STATE_DONE

  #-----------------------------------------------------------------------
  # Tick
  #-----------------------------------------------------------------------

  def line_trace( s ):

    state_str = "?"
    if s.state == s.STATE_LOAD:
      state_str = "L"
    if s.state == s.STATE_RUN:
      state_str = "R"
    if s.state == s.STATE_DONE:
      state_str = "D"

    return "({})" \
      .format( state_str )
