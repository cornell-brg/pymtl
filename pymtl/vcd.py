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
        print >> f, "s%s %s %s" % (hex(s._val), s._code, s.name)
    print >> f, "$end"

########################################################################
# End Code Borrowed from MyHDL 0.7
########################################################################

from test_examples import *
model = RegisterSplitter(8)
model.elaborate()

h = []

class Temp():
  pass

# Hacky attempt at generating a hierarchy in the form MyHDL code expects
def recurse_models(m, l):
  t = Temp()
  t.name = m.name
  t.level = l
  t.sigdict = {}
  t.memdict = {}
  # get signals
  for sig in m._ports:
    sig._val = 8  # TODO: temporary
    sig._tracing = None  # TODO: temporary
    t.sigdict[sig.name] = sig
  # add to hierarchy
  h.append( t )

  # recurse
  for subm in m._submodules:
    recurse_models( subm, l+1 )

recurse_models(model, 0)
#for x in h:
#  print x.name, x.level

# Print out our VCD
import sys
_writeVcdHeader( sys.stdout )
_writeVcdSigs( sys.stdout, h )

import simulate
from simulate import *
simulate.dump_vcd = True
sim = SimulationTool(model)
sim.generate()
model.inp.value = 0b11110000
sim.cycle()
#print "  IN",  model.inp.value
#print "  .",   model.reg0.out.value
#print "  OUT", [x.value for x in model.out]
model.inp.value = 0b1111000011001010
sim.cycle()
#print "  IN",  model.inp.value
#print "  .",   model.reg0.out.value
#print "  OUT", [x.value for x in model.out]
model.inp.value = 0b0000000000000000
sim.cycle()
#print "  IN",  model.inp.value
#print "  .",   model.reg0.out.value
#print "  OUT", [x.value for x in model.out]
model.inp.value = 0b0000011111110000
sim.cycle()
#print "  IN",  model.inp.value
#print "  .",   model.reg0.out.value
#print "  OUT", [x.value for x in model.out]
