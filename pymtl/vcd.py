########################################################################
# Begin Code Borrowed from MyHDL 0.7
########################################################################
import time

def _writeVcdHeader(f):
    print >> f, "$date"
    print >> f, "    %s" % time.asctime()
    print >> f, "$end"
    print >> f, "$version"
    #print >> f, "    PyMTL %s" % __version__
    print >> f, "    PyMTL ?.??"
    print >> f, "$end"
    print >> f, "$timescale"
    print >> f, "    1ns"
    print >> f, "$end"
    print >> f

def _genNameCode():
    n = 0
    while 1:
        yield _namecode(n)
        n += 1

_codechars = ""
for i in range(33, 127):
    _codechars += chr(i)
_mod = len(_codechars)

def _namecode(n):
    q, r = divmod(n, _mod)
    code = _codechars[r]
    while q > 0:
        q, r = divmod(q, _mod)
        code = _codechars[r] + code
    return code


def _writeVcdSigs(f, hierarchy):
    curlevel = 0
    namegen = _genNameCode()
    siglist = []
    for inst in hierarchy:
        level = inst.level
        name = inst.name
        sigdict = inst.sigdict
        memdict = inst.memdict
        delta = curlevel - level
        curlevel = level
        assert(delta >= -1)
        if delta >= 0:
            for i in range(delta + 1):
                print >> f, "$upscope $end"
        print >> f, "$scope module %s $end" % name
        for n, s in sigdict.items():
            # TODO: add _val field?
            if s._val == None:
                raise ValueError("%s of module %s has no initial value" % (n, name))
            if not s._tracing:
                s._tracing = 1
                s._code = namegen.next()
                siglist.append(s)
            # TODO: edited this
            #w = s._nrbits
            w = s.width
            if w:
                if w == 1:
                    print >> f, "$var reg 1 %s %s $end" % (s._code, n)
                else:
                    print >> f, "$var reg %s %s %s $end" % (w, s._code, n)
            else:
                print >> f, "$var real 1 %s %s $end" % (s._code, n)
    for i in range(curlevel):
        print >> f, "$upscope $end"
    print >> f
    print >> f, "$enddefinitions $end"
    print >> f, "$dumpvars"
    for s in siglist:
        # TODO: edited this
        #s._printVcd() # initial value
        # DEBUG
        #print >> f, "s%s %s %s" % (hex(s._val), s._code, s.name)
        # TODO: do real initialization
        if s.width == 1:
          print >> f, "%d%s" % (s.value.uint, s._code)
        else:
          print >> f, "s%s %s" % (s.value.uint, s._code)
    print >> f, "$end"

########################################################################
# End Code Borrowed from MyHDL 0.7
########################################################################
import sys

class _MyHDLNode():
  """A hacky container for use in the MyHDL VCD dump methods."""
  pass


class VCDUtil():

  """Hidden class used by the simulator tool for generating VCD output.

  This class takes a SimulationTool instance and augments it to generate
  VCD output.
  """
  def __init__(self, simulator, outfile=None):
    self.simulator = simulator
    self.hierarchy = []
    if not outfile:
      self.o = sys.stdout
    elif isinstance(outfile, str):
      self.o = open( outfile, 'w' )
    else:
      self.o = outfile
    simulator.vcd = True
    simulator.o   = self.o

    self.recurse_models( simulator.model, 0 )

    _writeVcdHeader( self.o )
    _writeVcdSigs( self.o, self.hierarchy )

  # Hacky attempt at generating a hierarchy in the form MyHDL code expects
  def recurse_models(self, model, level):
    t = _MyHDLNode()
    t.name = model.name
    t.level = level
    t.sigdict = {}
    t.memdict = {}
    # get signals
    signals = model._ports + model._wires
    for signal in signals:
      signal._val = signal.value.uint  # TODO: temporary
      signal._tracing = None  # TODO: temporary
      t.sigdict[signal.name] = signal
    # add to hierarchy
    self.hierarchy.append( t )

    # recurse
    for submodel in model._submodules:
      self.recurse_models( submodel, level+1 )


