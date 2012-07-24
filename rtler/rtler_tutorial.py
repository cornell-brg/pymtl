from rtler_vbase import VerilogModule, InPort, OutPort
from rtler_simulate import posedge_clk

class Register(VerilogModule):
  """A leaf module containing synchronous logic."""
  def __init__(self, bits):
    # Ports
    self.inp = InPort(bits)
    self.out = OutPort(bits)
  @posedge_clk
  def tick(self):
    inp = self.inp
    out = self.out
    out <<= inp

class RegisterWrapper(VerilogModule):
  """A structure module containing no logic."""
  def __init__(self, bits):
    # Ports
    self.inp = InPort(bits)
    self.out = OutPort(bits)
    # Submodules
    self.reg = Register(bits)
    # Connections
    self.inp <> self.reg.inp
    self.out <> self.reg.out


# Only execute this code if we execute this file directly
if __name__ == '__main__':

  # Creating a model instance
  model_instance = RegisterWrapper(8)

  # Elaborating the model
  model_instance.elaborate()

  # Inspect our model
  import rtler_debug
  rtler_debug.port_walk( model_instance )
