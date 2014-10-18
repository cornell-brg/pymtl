from new_pymtl import *
from new_pmlib import InValRdyBundle, OutValRdyBundle

class MyStruct( BitStructDefinition ):

  def __init__( s, nbits):

    # Specify fields

    s.src     = BitField( nbits)
    s.dest    = BitField( nbits )

class BasicModel( Model ):

    def __init__(s):

      s.ms    = MyStruct(16)
      s.input = InValRdyBundle(s.ms)
      s.out   = OutValRdyBundle(s.ms)

    def elaborate_logic(s):

      @s.combinational
      def logic():
        print "HERE"
        print s.input.msg
        s.out.msg.src.value  = s.input.msg.dest
        s.out.msg.dest.value = s.input.msg.src
        print s.out.msg
