from new_pymtl        import *
from new_pymtl  import *
from BugStruct import *
from new_pmlib import InValRdyBundle, OutValRdyBundle

class TH( Model ):

  def __init__(s):
    s.toy = BasicModel()
    s.input = InValRdyBundle(32)
    s.out = OutValRdyBundle(32)

  def elaborate_logic(s):

    s.connect(s.input, s.toy.input)
    s.connect(s.out, s.toy.out)


def test():

  model = TH()
  model.elaborate()
  sim = SimulationTool( model )

  sim.reset()

  model.input.msg.value = 0x12345678
  sim.cycle()
  assert model.out.msg == 0x56781234  
